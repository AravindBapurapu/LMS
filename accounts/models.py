from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User
from django.conf import settings
from adminstrator.models import CourseContent
from django.db import models

class Accounts(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('course_enroller', 'Course Enroller'),
        ('administrator', 'Administrator'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        CourseContent,
        on_delete=models.CASCADE
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    is_paid = models.BooleanField(default=False)

    # 🔥 Add these fields
    order_id = models.CharField(max_length=200, null=True, blank=True)
    payment_id = models.CharField(max_length=200, null=True, blank=True)
    signature = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.course.title}"


class PaymentTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseContent, on_delete=models.CASCADE)

    card_last4 = models.CharField(max_length=4)
    card_holder = models.CharField(max_length=200)

    transaction_id = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.course.title} - {self.status}"


# class Profile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE
#     )
#     avatar = models.ImageField(
#         upload_to='avatars/',
#         default='avatars/default.png'
#     )
#     bio = models.TextField(blank=True)
#     phone = models.CharField(max_length=15, blank=True)

#     def __str__(self):
#         return self.user.username
from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)




# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from .models import Profile

# @login_required
# def update_profile(request):

#     if request.method == "POST":

#         user = request.user
#         profile, created = Profile.objects.get_or_create(user=user)

#         # ---- Update username ----
#         username = request.POST.get("username")
#         if username:
#             user.username = username
#             user.save()

#         # ---- Update avatar ----
#         if request.FILES.get("avatar"):
#             profile.avatar = request.FILES.get("avatar")
#             profile.save()

#             return JsonResponse({
#                 "success": True,
#                 "avatar_url": profile.avatar.url
#             })

#         profile.save()

#         return JsonResponse({
#             "success": True,
#             "avatar_url": profile.avatar.url
#         })

#     return JsonResponse({"success": False})