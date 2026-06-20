from django.urls import path
# from .views import divya, course_carousel, course_videos, courses
from .views import *
from accounts.views import *

app_name = "sandhya"

urlpatterns = [
    path("dashboard/", divya, name="demo"),
    path("courses/", course_carousel, name="indi_courses"),
    path("all_courses/", courses, name="allCourses"),
    path("history/", history, name="history"),
    path("courses/<int:course_id>/", course_videos, name="course_videos"),
    path('update-profile/', update_profile, name='update_profile'),
]
