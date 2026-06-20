from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from adminstrator.views import *
from faculty.models import *
import random


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            # user.set_password(form.cleaned_data['password'])
            user.save()  # ✅ Saved in Accounts table

            return redirect('accounts:login')

    else:
        form = RegisterForm()

    return render(request, 'accounts/registration.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect_by_role(user)

    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


def redirect_by_role(user):
    if user.role == "student":
        return redirect("sandhya:demo")
    if user.role == "faculty":
        return redirect("faculty:faculty_home")
    if user.role == "course_enroller":
        return redirect("course_enroller:dashboard")
    if user.is_superuser:
        return redirect("adminstrator:dashboard")
    
# enrollment
# from .models import Enrollment

# def course_videos(request, course_id):
#     course = CourseContent.objects.get(id=course_id)
#     videos = CourseMedia.objects.filter(course=course)

#     is_enrolled = False

#     if request.user.is_authenticated:
#         is_enrolled = Enrollment.objects.filter(
#             user=request.user,
#             course=course,
#             is_paid=True
#         ).exists()

#     return render(request, "course_videos.html", {
#         "course": course,
#         "videos": videos,
#         "is_enrolled": is_enrolled
#     })

# from django.shortcuts import redirect
# from accounts.models import *

# def enroll_course(request, course_id):
#     course = CourseContent.objects.get(id=course_id)

#     if not request.user.is_authenticated:
#         return redirect("accounts:login")

#     enrollment, created = Enrollment.objects.get_or_create(
#         user=request.user,
#         course=course
#     )

#     # Redirect to payment page
#     return redirect("accounts:payment_page", course_id=course.id)

# def payment_page(request, course_id):
#     course = get_object_or_404(CourseContent, id=course_id)

#     return render(request, "payment.html", {
#         "course": course
#     })

# def payment_success(request, course_id):
#     enrollment = Enrollment.objects.get(
#         user=request.user,
#         course_id=course_id
#     )

#     enrollment.is_paid = True
#     enrollment.save()

#     return redirect("all_courses", course_id=course_id)




# mail testing

def test_mail(request):
    send_mail(
        subject="Test Mail from LMS",
        message="This is a test email",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=["receiver@gmail.com"],
        fail_silently=False,
    )
    return HttpResponse("Mail sent")

# send otp

def send_otp(request):
    email = request.POST.get("email")

    otp = random.randint(100000, 999999)

    request.session["email_otp"] = str(otp)
    request.session["otp_email"] = email

    send_mail(
        subject="Your LMS OTP",
        message=f"Your OTP is {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

    return JsonResponse({"status": "otp_sent"})


# varify otp
def verify_otp(request):
    user_otp = request.POST.get("otp")

    if user_otp == request.session.get("email_otp"):
        return JsonResponse({"status": "verified"})
    else:
        return JsonResponse({"status": "invalid"})


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def update_profile(request):

    if request.method == "POST":

        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)

        username = request.POST.get("username")

        if username:
            user.username = username
            user.save()

        if request.FILES.get("avatar"):
            profile.avatar = request.FILES.get("avatar")

        profile.save()

        return JsonResponse({
            "success": True,
            "avatar_url": profile.avatar.url
        })

    return JsonResponse({"success": False})

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password

@login_required
def change_password(request):

    if request.method == "POST":

        user = request.user
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not user.check_password(current_password):
            return JsonResponse({"success": False, "error": "Wrong current password"})

        if new_password != confirm_password:
            return JsonResponse({"success": False, "error": "Passwords do not match"})

        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})
