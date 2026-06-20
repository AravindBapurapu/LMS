from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import CourseContent, CourseMedia
from accounts.models import Enrollment
from django.contrib import messages
import json

def adminstrator(request):
    return render(request, "adminstrator/home.html")

def enoll(request):
    return render(request, "adminstrator/enroll.html")

from django.shortcuts import render

def admin_dashboard(request):
    return render(request, "adminstrator/admin_dashboard.html")

def manage_course(request):
    return render(request, "adminstrator/manage_course.html")

def manage_student(request):
    return render(request, "adminstrator/manage_student.html")

def manage_faculty(request):
    return render(request, "adminstrator/manage_faculty.html")

def report_analysis(request):
    return render(request, "adminstrator/report_analysis.html")


@require_POST
def save_courses(request):
    try:
        courses = json.loads(request.POST.get("courses", "[]"))
        response_courses = []

        for c_index, course in enumerate(courses):
            course_id = course.get("id")
            thumbnail = request.FILES.get(f"thumbnail_{c_index}")

            if course_id:
                obj = CourseContent.objects.get(id=course_id)
                obj.title = course["title"]
                obj.price = course["price"]
                obj.description = course["description"]
                obj.video_links = course.get("video_links", [])
                if thumbnail:
                    obj.thumbnail = thumbnail
                obj.save()

                # ❗ Clear old media safely
                CourseMedia.objects.filter(course=obj).delete()
            else:
                obj = CourseContent.objects.create(
                    title=course["title"],
                    price=course["price"],
                    description=course["description"],
                    video_links=course.get("video_links", []),
                    thumbnail=thumbnail
                )

            # ✅ SAVE VIDEO + IMAGE PROPERLY
            for video in course.get("video_links", []):
                client_index = video.get("client_index")
                image = request.FILES.get(
                    f"video_image_{c_index}_{client_index}"
                )

                CourseMedia.objects.create(
                    course=obj,
                    video_url=video["video_url"],
                    image=image
                )

            response_courses.append({
                "id": obj.id,
                "thumbnail_url": (
                    request.build_absolute_uri(obj.thumbnail.url)
                    if obj.thumbnail else None
                )
            })

        return JsonResponse({
            "status": "success",
            "courses": response_courses
        })

    except Exception as e:
        print("🔥 SAVE COURSES ERROR:", repr(e))
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)



@require_POST
def delete_course(request, pk):
    try:
        CourseContent.objects.filter(id=pk).delete()
        return JsonResponse({"status": "success", "message": "Course deleted"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

def get_courses(request):
    courses = CourseContent.objects.all()
    data = []

    for course in courses:
        data.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            # "video_links": list(course.media.values_list("video_url", flat=True)),
            
            "video_links": [
                {
                    "video_url": media.video_url,
                    "image_url": (
                        request.build_absolute_uri(media.image.url)
                        if media.image else None
                    )
                }
                for media in course.media.all()
            ],
            
            "price": str(course.price),
            "thumbnail_url": (
                request.build_absolute_uri(course.thumbnail.url)
                if course.thumbnail else None
            )
        })

    return JsonResponse(data, safe=False)


def enroll_course(request, course_id):
    course = CourseContent.objects.get(id=course_id)

    if not request.user.is_authenticated:
        return redirect("accounts:login")

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    # Redirect to payment page
    return redirect("accounts:payment_page", course_id=course.id)


import uuid
import hashlib
from django.conf import settings

@login_required
def payment_page(request, course_id):
    course = get_object_or_404(CourseContent, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    # Create Fake Razorpay Order
    if not enrollment.order_id:
        enrollment.order_id = "order_" + str(uuid.uuid4().hex[:12])
        enrollment.save()

    return render(request, "accounts/payment.html", {
        "course": course,
        "enrollment": enrollment,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })

@login_required
def fake_payment_gateway(request, course_id):
    course = get_object_or_404(CourseContent, id=course_id)

    enrollment = Enrollment.objects.get(
        user=request.user,
        course=course
    )

    return render(request, "accounts/fake_gateway.html", {
        "course": course,
        "enrollment": enrollment
    })

@login_required
def verify_payment(request, course_id):
    course = get_object_or_404(CourseContent, id=course_id)

    enrollment = Enrollment.objects.get(
        user=request.user,
        course=course
    )

    payment_id = request.POST.get("payment_id")
    order_id = request.POST.get("order_id")
    signature = request.POST.get("signature")

    # 🔥 Create expected signature
    generated_signature = hashlib.sha256(
        f"{order_id}|{payment_id}{settings.RAZORPAY_SECRET}".encode()
    ).hexdigest()

    if signature == generated_signature:
        enrollment.payment_id = payment_id
        enrollment.signature = signature
        enrollment.is_paid = True
        enrollment.save()

        messages.success(request, "🎉 Payment Verified Successfully!")
        return redirect("student:course_videos", course_id=course.id)

    else:
        messages.error(request, "❌ Payment Verification Failed")
        return redirect("adminstrator:payment_page", course_id=course.id)


import uuid
from accounts.models import PaymentTransaction

@login_required
def process_payment(request, course_id):

    course = get_object_or_404(CourseContent, id=course_id)

    if request.method == "POST":

        card_holder = request.POST.get("card_holder")
        card_number = request.POST.get("card_number")
        expiry = request.POST.get("expiry")
        cvv = request.POST.get("cvv")

        # 🔥 Basic Fake Validation

        if len(card_number) != 16 or not card_number.isdigit():
            messages.error(request, "Invalid Card Number")
            return redirect("adminstrator:fake_payment", course_id=course.id)

        if len(cvv) != 3:
            messages.error(request, "Invalid CVV")
            return redirect("adminstrator:fake_payment", course_id=course.id)

        # 🔥 Simulate Payment Success (You can randomize this)
        transaction_id = "txn_" + uuid.uuid4().hex[:10]

        payment = PaymentTransaction.objects.create(
            user=request.user,
            course=course,
            card_last4=card_number[-4:],
            card_holder=card_holder,
            transaction_id=transaction_id,
            status="success"
        )

        # 🔥 Unlock Course
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )

        enrollment.is_paid = True
        enrollment.save()

        messages.success(request, "🎉 Payment Successful! Course Unlocked.")

        return redirect("sandhya:course_videos", course_id=course.id)




from accounts.models import Accounts
from faculty.models import FacultyApplication, FacultyProfile
from django.utils import timezone


def manage_faculty(request):
    applications = FacultyApplication.objects.select_related('user').all().order_by('-applied_on')
    return render(
        request,
        "adminstrator/manage_faculty.html",
        {"applications": applications}
    )


def approve_faculty(request, pk):
    application = get_object_or_404(FacultyApplication, id=pk)
    application.status = "approved"
    application.save()

    faculty_profile, created = FacultyProfile.objects.get_or_create(
        user=application.user,
        defaults={
            'phone': application.phone or '',
            'qualification': application.qualification,
            'expertise': application.expertise,
            'bio': application.bio,
            'experience': application.experience,
            'is_approved': True,
            'approved_on': timezone.now(),
        }
    )

    if not created:
        faculty_profile.phone = application.phone or faculty_profile.phone
        faculty_profile.qualification = application.qualification
        faculty_profile.expertise = application.expertise
        faculty_profile.bio = application.bio
        faculty_profile.experience = application.experience
        faculty_profile.is_approved = True
        faculty_profile.approved_on = timezone.now()
        faculty_profile.save()

    application.user.role = 'faculty'
    application.user.save()

    messages.success(request, "Faculty application approved.")
    return redirect("adminstrator:faculty_manage")


def reject_faculty(request, pk):
    application = get_object_or_404(FacultyApplication, id=pk)
    application.status = "rejected"
    application.save()
    messages.info(request, "Faculty application rejected.")
    return redirect("adminstrator:faculty_manage")