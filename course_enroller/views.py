from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg, Count
from django.utils import timezone
from decimal import Decimal
import uuid

from accounts.models import Accounts, Enrollment, PaymentTransaction
from adminstrator.models import CourseContent, CourseMedia
from .models import (
    EnrollerProfile, PaymentMethod, EnrollmentPayment, 
    VideoWatchHistory, EnrollmentCertificate, EnrollerReview
)
from .forms import (
    EnrollerRegistrationForm, EnrollerLoginForm, EnrollerProfileForm,
    PaymentMethodForm, EnrollmentForm, EnrollerReviewForm, CourseSearchForm
)


# ==================== Authentication Views ====================

def enroller_register(request):
    """Course enroller registration"""
    if request.user.is_authenticated:
        return redirect('course_enroller:dashboard')
    
    if request.method == 'POST':
        form = EnrollerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create enroller profile
            EnrollerProfile.objects.create(user=user)
            messages.success(request, "Registration successful! Please login.")
            return redirect('accounts:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = EnrollerRegistrationForm()
    
    return render(request, 'course_enroller/register.html', {'form': form})


def enroller_login(request):
    """Course enroller login"""
    if request.user.is_authenticated:
        return redirect('course_enroller:dashboard')
    
    if request.method == 'POST':
        form = EnrollerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                user = Accounts.objects.get(username=username, role='course_enroller')
                if user.check_password(password):
                    from django.contrib.auth import login
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect('course_enroller:dashboard')
            except Accounts.DoesNotExist:
                messages.error(request, "Invalid credentials!")
    else:
        form = EnrollerLoginForm()
    
    return render(request, 'course_enroller/login.html', {'form': form})


# ==================== Dashboard Views ====================

@login_required
def dashboard(request):
    """Enroller dashboard"""
    if request.user.role != 'course_enroller':
        messages.error(request, "Access denied. Course Enroller only.")
        return redirect('accounts:login')
    
    try:
        enroller_profile = EnrollerProfile.objects.get(user=request.user)
    except EnrollerProfile.DoesNotExist:
        enroller_profile = EnrollerProfile.objects.create(user=request.user)
    
    # Get enrolled courses
    enrollments = Enrollment.objects.filter(
        user=request.user, 
        is_paid=True
    ).select_related('course').order_by('-enrolled_at')
    
    # Get statistics
    total_enrolled = enrollments.count()
    total_spent = sum(e.course.price for e in enrollments)
    
    # Get recent activity
    recent_watchings = VideoWatchHistory.objects.filter(
        enrollment__user=request.user
    ).select_related('video', 'enrollment__course').order_by('-last_watched_at')[:5]
    
    # Get certificates earned
    certificates = EnrollmentCertificate.objects.filter(
        enrollment__user=request.user
    ).order_by('-issued_date')
    
    # Recommend courses (courses user hasn't enrolled in)
    all_courses = CourseContent.objects.all()
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    recommended = all_courses.exclude(id__in=enrolled_course_ids)[:6]
    
    context = {
        'enroller_profile': enroller_profile,
        'enrollments': enrollments[:6],  # Show recent 6
        'total_enrolled': total_enrolled,
        'total_spent': total_spent,
        'certificates_count': certificates.count(),
        'recent_watchings': recent_watchings,
        'recommended_courses': recommended,
    }
    
    return render(request, 'course_enroller/dashboard.html', context)


# ==================== Course Views ====================

def browse_courses(request):
    """Browse all available courses"""
    courses = CourseContent.objects.all()
    form = CourseSearchForm(request.GET or None)
    
    # Apply search filter
    if request.GET.get('search'):
        search = request.GET.get('search')
        courses = courses.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Apply price filter
    if request.GET.get('price_filter'):
        price_filter = request.GET.get('price_filter')
        if price_filter == '0-500':
            courses = courses.filter(price__lte=500)
        elif price_filter == '500-1000':
            courses = courses.filter(price__gte=500, price__lte=1000)
        elif price_filter == '1000-5000':
            courses = courses.filter(price__gte=1000, price__lte=5000)
        elif price_filter == '5000+':
            courses = courses.filter(price__gte=5000)
    
    # Apply sorting
    sort_by = request.GET.get('sort_by', '-created_at')
    if sort_by:
        courses = courses.order_by(sort_by)
    
    # Add enrollment and review info
    for course in courses:
        course.enrolled_count = Enrollment.objects.filter(
            course=course, 
            is_paid=True
        ).count()
        
        reviews = EnrollerReview.objects.filter(
            enrollment__course=course
        )
        if reviews.exists():
            course.avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            course.review_count = reviews.count()
        else:
            course.avg_rating = 0
            course.review_count = 0
        
        # Check if user already enrolled
        if request.user.is_authenticated:
            course.is_enrolled = Enrollment.objects.filter(
                user=request.user, 
                course=course, 
                is_paid=True
            ).exists()
        else:
            course.is_enrolled = False
    
    context = {
        'courses': courses,
        'form': form,
        'search_term': request.GET.get('search', ''),
    }
    
    return render(request, 'course_enroller/browse_courses.html', context)


def course_detail(request, course_slug):
    """Detailed view of a single course"""
    course = get_object_or_404(CourseContent, slug=course_slug)
    videos = CourseMedia.objects.filter(course=course)
    
    # Get reviews and ratings
    reviews = EnrollerReview.objects.filter(
        enrollment__course=course
    ).select_related('enrollment__user')
    
    avg_rating = 0
    if reviews.exists():
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Check enrollment status
    is_enrolled = False
    user_review = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user, 
            course=course
        ).first()
        
        if enrollment:
            is_enrolled = enrollment.is_paid
            user_review = EnrollerReview.objects.filter(enrollment=enrollment).first()
    
    # Get course stats
    enrolled_count = Enrollment.objects.filter(
        course=course, 
        is_paid=True
    ).count()
    
    context = {
        'course': course,
        'videos': videos,
        'is_enrolled': is_enrolled,
        'reviews': reviews[:10],
        'avg_rating': avg_rating,
        'total_reviews': reviews.count(),
        'enrolled_count': enrolled_count,
        'user_review': user_review,
    }
    
    return render(request, 'course_enroller/course_detail.html', context)


# ==================== Enrollment & Payment Views ====================

@login_required
@require_POST
def enroll_course(request, course_slug):
    """Enroll user in a course"""
    if request.user.role != 'course_enroller':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    course = get_object_or_404(CourseContent, slug=course_slug)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(
        user=request.user, 
        course=course
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.is_paid:
            return JsonResponse({'status': 'error', 'message': 'Already enrolled in this course'})
    else:
        # Create new enrollment
        Enrollment.objects.create(user=request.user, course=course, is_paid=False)
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Please proceed to payment',
        'redirect': f'/course-enroller/payment/{course.slug}/'
    })


@login_required
def payment_page(request, course_slug):
    """Payment page for course enrollment"""
    if request.user.role != 'course_enroller':
        messages.error(request, "Access denied.")
        return redirect('course_enroller:browse')
    
    course = get_object_or_404(CourseContent, slug=course_slug)
    
    # Get or create enrollment
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, 
        course=course
    )
    
    if enrollment.is_paid:
        messages.info(request, "You already have access to this course.")
        return redirect('course_enroller:watch', course_slug=course_slug)
    
    # Get payment methods
    try:
        enroller_profile = EnrollerProfile.objects.get(user=request.user)
        payment_methods = PaymentMethod.objects.filter(enroller=enroller_profile)
    except EnrollerProfile.DoesNotExist:
        payment_methods = []
    
    # Generate transaction ID
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'payment_methods': payment_methods,
        'transaction_id': transaction_id,
        'razorpay_key': 'rzp_test_FAKE123456',  # From settings
    }
    
    return render(request, 'course_enroller/payment.html', context)


@login_required
@require_POST
def process_payment(request, enrollment_id):
    """Process payment for enrollment"""
    if request.user.role != 'course_enroller':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    
    if enrollment.is_paid:
        return JsonResponse({'status': 'error', 'message': 'Already paid'})
    
    try:
        # Get payment data
        payment_method_id = request.POST.get('payment_method_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        # Create payment record
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        
        payment = EnrollmentPayment.objects.create(
            enrollment=enrollment,
            amount=enrollment.course.price,
            transaction_id=transaction_id,
            status='processing',
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            razorpay_signature=razorpay_signature,
        )
        
        # Mark enrollment as paid
        enrollment.is_paid = True
        enrollment.payment_id = razorpay_payment_id
        enrollment.save()
        
        # Update payment status
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        payment.save()
        
        # Create payment transaction record
        PaymentTransaction.objects.create(
            user=request.user,
            course=enrollment.course,
            card_last4='****',
            card_holder=request.user.get_full_name() or request.user.username,
            transaction_id=transaction_id,
            status='success'
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Payment successful!',
            'redirect': f'/course-enroller/watch/{enrollment.course.slug}/'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ==================== Video Watching Views ====================

@login_required
def watch_video(request, course_slug):
    """Watch course videos"""
    if request.user.role != 'course_enroller':
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    course = get_object_or_404(CourseContent, slug=course_slug)
    
    # Check enrollment and payment
    enrollment = Enrollment.objects.filter(
        user=request.user, 
        course=course, 
        is_paid=True
    ).first()
    
    if not enrollment:
        messages.error(request, "You need to enroll and pay to access this course.")
        return redirect('course_enroller:course_detail', course_slug=course_slug)
    
    # Get videos
    videos = CourseMedia.objects.filter(course=course)
    
    # Get watch history
    watch_history = VideoWatchHistory.objects.filter(
        enrollment=enrollment
    ).select_related('video')
    
    # Get current video
    current_video_id = request.GET.get('video_id')
    current_video = None
    
    if current_video_id:
        current_video = get_object_or_404(CourseMedia, id=current_video_id, course=course)
        
        # Get or create watch history entry
        video_history, created = VideoWatchHistory.objects.get_or_create(
            enrollment=enrollment,
            video=current_video
        )
    elif videos.exists():
        current_video = videos.first()
        video_history, created = VideoWatchHistory.objects.get_or_create(
            enrollment=enrollment,
            video=current_video
        )
    
    context = {
        'course': course,
        'enrollment': enrollment,
        'videos': videos,
        'current_video': current_video,
        'watch_history': watch_history,
    }
    
    return render(request, 'course_enroller/watch_video.html', context)


@login_required
@require_POST
def update_watch_progress(request, video_id):
    """Update video watch progress"""
    if request.user.role != 'course_enroller':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    try:
        video = get_object_or_404(CourseMedia, id=video_id)
        watch_duration = int(request.POST.get('watch_duration', 0))
        total_duration = int(request.POST.get('total_duration', 0))
        
        # Get last enrollment (most recent)
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=video.course,
            is_paid=True
        ).last()
        
        if not enrollment:
            return JsonResponse({'status': 'error', 'message': 'Enrollment not found'}, status=403)
        
        # Update watch history
        video_history, created = VideoWatchHistory.objects.get_or_create(
            enrollment=enrollment,
            video=video
        )
        
        video_history.watch_duration = max(video_history.watch_duration, watch_duration)
        video_history.total_duration = total_duration
        
        # Mark as completed if watched 90%
        if total_duration > 0 and (watch_duration / total_duration) >= 0.9:
            video_history.is_completed = True
        
        video_history.save()
        
        return JsonResponse({
            'status': 'success',
            'completion_percentage': video_history.get_completion_percentage()
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ==================== My Enrollments Views ====================

@login_required
def my_enrollments(request):
    """Show all enrollments of the user"""
    if request.user.role != 'course_enroller':
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    enrollments = Enrollment.objects.filter(
        user=request.user, 
        is_paid=True
    ).select_related('course').order_by('-enrolled_at')
    
    # Add progress info
    for enrollment in enrollments:
        videos = CourseMedia.objects.filter(course=enrollment.course)
        if videos.exists():
            completed_videos = VideoWatchHistory.objects.filter(
                enrollment=enrollment,
                is_completed=True
            ).count()
            enrollment.progress_percentage = int((completed_videos / videos.count()) * 100)
        else:
            enrollment.progress_percentage = 0
    
    context = {
        'enrollments': enrollments,
    }
    
    return render(request, 'course_enroller/my_enrollments.html', context)


# ==================== Profile & Settings Views ====================

@login_required
def enroller_profile(request):
    """Enroller profile page"""
    if request.user.role != 'course_enroller':
        messages.error(request, "Access denied.")
        return redirect('accounts:login')
    
    try:
        enroller_profile = EnrollerProfile.objects.get(user=request.user)
    except EnrollerProfile.DoesNotExist:
        enroller_profile = EnrollerProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = EnrollerProfileForm(request.POST, request.FILES, instance=enroller_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('course_enroller:profile')
    else:
        form = EnrollerProfileForm(instance=enroller_profile)
    
    # Get statistics
    enrollments = Enrollment.objects.filter(user=request.user, is_paid=True)
    total_spent = sum(e.course.price for e in enrollments)
    certificates = EnrollmentCertificate.objects.filter(enrollment__user=request.user).count()
    
    context = {
        'enroller_profile': enroller_profile,
        'form': form,
        'total_enrolled': enrollments.count(),
        'total_spent': total_spent,
        'certificates': certificates,
    }
    
    return render(request, 'course_enroller/profile.html', context)


# ==================== Review Views ====================

@login_required
@require_POST
def add_review(request, enrollment_id):
    """Add review for a course"""
    if request.user.role != 'course_enroller':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    
    form = EnrollerReviewForm(request.POST)
    if form.is_valid():
        review, created = EnrollerReview.objects.get_or_create(
            enrollment=enrollment,
            defaults={
                'rating': form.cleaned_data['rating'],
                'review_text': form.cleaned_data['review_text']
            }
        )
        
        if not created:
            review.rating = form.cleaned_data['rating']
            review.review_text = form.cleaned_data['review_text']
            review.save()
        
        return JsonResponse({'status': 'success', 'message': 'Review submitted!'})
    
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


# ==================== Utility Views ====================

def index(request):
    """Redirect to appropriate homepage"""
    if request.user.is_authenticated:
        if request.user.role == 'course_enroller':
            return redirect('course_enroller:dashboard')
    return redirect('course_enroller:browse')

