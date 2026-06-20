from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q
import json

from .models import *
from .forms import *
from accounts.models import Accounts, Profile, Enrollment
from adminstrator.models import CourseContent, CourseMedia

@login_required
def faculty_dashboard(request):
    """Main dashboard for faculty"""
    if request.user.role != 'faculty':
        messages.error(request, "Access denied. Faculty only.")
        return redirect('accounts:login')
    
    try:
        faculty_profile, created = FacultyProfile.objects.get_or_create(user=request.user)
        if not faculty_profile.is_approved:
            return redirect('faculty:application_status')
        
        # Get stats
        total_courses = FacultyCourse.objects.filter(faculty=faculty_profile, is_active=True).count()
        total_materials = CourseMaterial.objects.filter(faculty_course__faculty=faculty_profile).count()
        
        # Get recent notifications
        recent_notifications = FacultyNotification.objects.filter(
            faculty=faculty_profile
        )[:5]
        
        context = {
            'faculty_profile': faculty_profile,
            'total_courses': total_courses,
            'total_materials': total_materials,
            'recent_notifications': recent_notifications,
        }
        return render(request, 'faculty/dashboard.html', context)
        
    except FacultyProfile.DoesNotExist:
        return redirect('faculty:faculty_home')

@login_required
def faculty_home(request):
    """Faculty home page with welcome message and apply button"""
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user)
        application = FacultyApplication.objects.filter(user=request.user).first()
        
        context = {
            'faculty_profile': faculty_profile,
            'application': application,
            'is_approved': faculty_profile.is_approved
        }
        return render(request, 'faculty/home.html', context)
        
    except FacultyProfile.DoesNotExist:
        # Check if application exists
        application = FacultyApplication.objects.filter(user=request.user).first()
        context = {
            'application': application,
            'is_approved': False
        }
        return render(request, 'faculty/home.html', context)

@login_required
def apply_faculty(request):
    """Handle faculty application via popup form"""
    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        try:
            form = FacultyApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                application = form.save(commit=False)
                application.user = request.user
                application.tech = application.expertise or ''
                application.save()
            
                send_mail(
                    subject="New Faculty Application",
                    message=f"A new faculty application has been submitted by {application.name}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=['admin@lms.com'],
                    fail_silently=True,
                )
                
                messages.success(request, "Application submitted successfully! We'll review it shortly.")
                if is_ajax:
                    return JsonResponse({'status': 'success', 'message': 'Application submitted'})
                return redirect('faculty:application_status')
            else:
                if is_ajax:
                    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
                messages.error(request, 'Please correct the highlighted fields and submit again.')
                return redirect('faculty:faculty_home')
        except Exception as e:
            error_message = str(e)
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {error_message}'}, status=500)
            messages.error(request, 'An unexpected server error occurred. Please try again.')
            return redirect('faculty:faculty_home')
    
    form = FacultyApplicationForm()
    return render(request, 'faculty/apply_popup.html', {'form': form})

@login_required
def application_status(request):
    """Check application status"""
    application = FacultyApplication.objects.filter(user=request.user).first()
    
    if not application:
        messages.warning(request, "You haven't applied yet.")
        return redirect('faculty:faculty_home')
    
    # Check if approved
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user)
        if faculty_profile.is_approved:
            messages.success(request, "Congratulations! Your application is approved.")
            return redirect('faculty:dashboard')
    except FacultyProfile.DoesNotExist:
        pass
    
    return render(request, 'faculty/application_status.html', {'application': application})

@login_required
def my_courses(request):
    """Show faculty's assigned courses"""
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user, is_approved=True)
        faculty_courses = FacultyCourse.objects.filter(
            faculty=faculty_profile, 
            is_active=True
        ).select_related('course')
        
        # Get student count for each course
        for fc in faculty_courses:
            fc.student_count = Enrollment.objects.filter(
                course=fc.course,
                is_paid=True
            ).count()
        
        context = {
            'faculty_profile': faculty_profile,
            'faculty_courses': faculty_courses
        }
        return render(request, 'faculty/my_courses.html', context)
        
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found or not approved.")
        return redirect('faculty:faculty_home')

@login_required
def course_detail(request, course_id):
    """Show detailed view of a course with materials"""
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user, is_approved=True)
        faculty_course = get_object_or_404(
            FacultyCourse, 
            faculty=faculty_profile,
            course_id=course_id,
            is_active=True
        )
        
        course = faculty_course.course
        materials = CourseMaterial.objects.filter(faculty_course=faculty_course)
        
        # Get enrolled students
        enrollments = Enrollment.objects.filter(
            course=course,
            is_paid=True
        ).select_related('user')
        
        context = {
            'faculty_profile': faculty_profile,
            'faculty_course': faculty_course,
            'course': course,
            'materials': materials,
            'enrollments': enrollments,
            'material_form': CourseMaterialForm()
        }
        return render(request, 'faculty/course_detail.html', context)
        
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect('faculty:faculty_home')

@login_required
def add_material(request, course_id):
    """Add material to a course"""
    if request.method == 'POST':
        try:
            faculty_profile = FacultyProfile.objects.get(user=request.user, is_approved=True)
            faculty_course = get_object_or_404(
                FacultyCourse, 
                faculty=faculty_profile,
                course_id=course_id,
                is_active=True
            )
            
            form = CourseMaterialForm(request.POST, request.FILES)
            if form.is_valid():
                material = form.save(commit=False)
                material.faculty_course = faculty_course
                material.save()
                
                messages.success(request, "Material added successfully!")
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def edit_material(request, material_id):
    """Edit course material"""
    material = get_object_or_404(CourseMaterial, id=material_id)
    
    # Check permission
    if material.faculty_course.faculty.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, "Material updated successfully!")
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
    # Return form for GET request
    form = CourseMaterialForm(instance=material)
    return render(request, 'faculty/edit_material_popup.html', {'form': form, 'material': material})

@login_required
def delete_material(request, material_id):
    """Delete course material"""
    material = get_object_or_404(CourseMaterial, id=material_id)
    
    # Check permission
    if material.faculty_course.faculty.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        material.delete()
        messages.success(request, "Material deleted successfully!")
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def add_records(request):
    """Show faculty's teaching records and student performance"""
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user, is_approved=True)
        faculty_courses = FacultyCourse.objects.filter(
            faculty=faculty_profile,
            is_active=True
        ).select_related('course')
        
        records_data = []
        for fc in faculty_courses:
            students = Enrollment.objects.filter(
                course=fc.course,
                is_paid=True
            ).select_related('user')
            
            # You can add more student performance metrics here
            records_data.append({
                'course': fc.course,
                'student_count': students.count(),
                'students': students[:5]  # Show first 5 students
            })
        
        context = {
            'faculty_profile': faculty_profile,
            'records_data': records_data
        }
        return render(request, 'faculty/add_records.html', context)
        
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect('faculty:faculty_home')

@login_required
def course_students(request, course_id):
    """Show all students in a specific course"""
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user, is_approved=True)
        faculty_course = get_object_or_404(
            FacultyCourse, 
            faculty=faculty_profile,
            course_id=course_id,
            is_active=True
        )
        
        enrollments = Enrollment.objects.filter(
            course=faculty_course.course,
            is_paid=True
        ).select_related('user')
        
        context = {
            'faculty_profile': faculty_profile,
            'faculty_course': faculty_course,
            'enrollments': enrollments
        }
        return render(request, 'faculty/course_students.html', context)
        
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect('faculty:faculty_home')

@login_required
def guidelines(request):
    """Show faculty guidelines"""
    guidelines = FacultyGuideline.objects.filter(is_active=True)
    
    # For faculty users, also show their profile
    faculty_profile = None
    try:
        if request.user.role == 'faculty':
            faculty_profile = FacultyProfile.objects.get(user=request.user)
    except FacultyProfile.DoesNotExist:
        pass
    
    context = {
        'guidelines': guidelines,
        'faculty_profile': faculty_profile
    }
    return render(request, 'faculty/guidelines.html', context)

@login_required
def faculty_contact(request):
    """Show faculty contact information"""
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user, is_approved=True)
        contact_info, created = FacultyContact.objects.get_or_create(faculty=faculty_profile)
        
        # Also show admin contact
        admin_contacts = Accounts.objects.filter(
            Q(role='administrator') | Q(is_superuser=True)
        ).select_related('profile')
        
        context = {
            'faculty_profile': faculty_profile,
            'contact_info': contact_info,
            'admin_contacts': admin_contacts,
            'contact_form': FacultyContactForm(instance=contact_info)
        }
        return render(request, 'faculty/contact.html', context)
        
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Access denied.")
        return redirect('faculty:faculty_home')

@login_required
def update_contact(request):
    """Update faculty contact information"""
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user, is_approved=True)
        contact_info, created = FacultyContact.objects.get_or_create(faculty=faculty_profile)
        
        if request.method == 'POST':
            form = FacultyContactForm(request.POST, instance=contact_info)
            if form.is_valid():
                form.save()
                messages.success(request, "Contact information updated successfully!")
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def faculty_profile(request):
    """Show faculty profile with settings"""
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user, is_approved=True)
        profile, created = Profile.objects.get_or_create(user=request.user)
        contact_info, created = FacultyContact.objects.get_or_create(faculty=faculty_profile)
        
        context = {
            'faculty_profile': faculty_profile,
            'profile': profile,
            'contact_info': contact_info,
            'profile_form': FacultyProfileForm(instance=faculty_profile),
            'contact_form': FacultyContactForm(instance=contact_info)
        }
        return render(request, 'faculty/profile.html', context)
        
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('faculty:faculty_home')

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect
from accounts.models import Profile
from .models import FacultyProfile


@login_required
def update_faculty_profile(request):

    if request.method == "POST":

        faculty_profile, created = FacultyProfile.objects.get_or_create(
            user=request.user
        )

        profile, created = Profile.objects.get_or_create(
            user=request.user
        )

        username = request.POST.get("username")
        bio = request.POST.get("bio")

        if username:
            request.user.username = username
            request.user.save()

        if bio:
            faculty_profile.bio = bio
            faculty_profile.save()

        # avatar upload
        if request.FILES.get("avatar"):
            profile.avatar = request.FILES["avatar"]
            profile.save()

        # password change
        current = request.POST.get("current_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        if current and new and confirm:

            if not request.user.check_password(current):
                messages.error(request, "Current password incorrect")
                return redirect("faculty:faculty_home")

            if new != confirm:
                messages.error(request, "Passwords do not match")
                return redirect("faculty:faculty_home")

            request.user.set_password(new)
            request.user.save()

            update_session_auth_hash(request, request.user)

        messages.success(request, "Profile updated successfully")

        return redirect("faculty:faculty_home")

    return redirect("faculty:faculty_home")
@login_required
def notifications(request):
    """Show faculty notifications"""
    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user)
        notifications_list = FacultyNotification.objects.filter(faculty=faculty_profile)
        
        # Mark as read when viewed
        notifications_list.filter(is_read=False).update(is_read=True)
        
        context = {
            'faculty_profile': faculty_profile,
            'notifications': notifications_list
        }
        return render(request, 'faculty/notifications.html', context)
        
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('faculty:faculty_home')

@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = get_object_or_404(FacultyNotification, id=notification_id)
        if notification.faculty.user == request.user:
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    


@login_required
def get_notifications(request):

    try:
        faculty_profile = FacultyProfile.objects.get(user=request.user)

        notifications = FacultyNotification.objects.filter(
            faculty=faculty_profile,
            is_read=False
        )[:10]

        data = []

        for n in notifications:
            data.append({
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "created_at": n.created_on.strftime("%d %b %H:%M")
            })

        return JsonResponse({
            "notifications": data
        })

    except:
        return JsonResponse({
            "notifications": []
        })