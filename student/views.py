from django.shortcuts import render
from adminstrator.models import CourseContent, CourseMedia
# from adminstrator.models import CourseContent, CourseMedia
from django.shortcuts import get_object_or_404


# def divya(request):
#     return render(request, "student/index.html")

def divya(request):
    courses = CourseContent.objects.all()
    return render(request, "student/index.html", {
        "courses": courses
    })


def course_carousel(request):
    courses = CourseContent.objects.all()
    return render(request, "student/individual_courses.html", {
        "courses": courses
    })

def history(request):
    courses = CourseContent.objects.all()
    return render(request, 'student/history.html',{
        "courses":courses
    })

# Create your models here.
def courses(request):
    courses = CourseContent.objects.all()
    return render(request, "student/courses.html", {
        "courses": courses
    })


#     return None
def get_embed_url(url):
    if not url:
        return None

    # watch?v=
    if "youtube.com/watch?v=" in url:
        video_id = url.split("watch?v=")[1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    # youtu.be
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    return None

from accounts.models import Enrollment
from django.contrib import messages

def course_videos(request, course_id):

    course = get_object_or_404(CourseContent, id=course_id)
    videos = CourseMedia.objects.filter(course=course)

    is_enrolled = False

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
            is_paid=True
        ).exists()

    return render(request, "student/all_courses.html", {
        "course": course,
        "videos": videos,
        "is_enrolled": is_enrolled
    })
