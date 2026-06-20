from django.urls import path
from .views import *

app_name = "course_enroller"

urlpatterns = [
    # Authentication
    path("register/", enroller_register, name="register"),
    path("login/", enroller_login, name="login"),
    
    # Dashboard
    path("dashboard/", dashboard, name="dashboard"),
    
    # Courses
    path("browse/", browse_courses, name="browse"),
    path("course/<slug:course_slug>/", course_detail, name="course_detail"),
    
    # Enrollment & Payment
    path("enroll/<slug:course_slug>/", enroll_course, name="enroll"),
    path("payment/<slug:course_slug>/", payment_page, name="payment"),
    path("process-payment/<int:enrollment_id>/", process_payment, name="process_payment"),
    
    # Video Watching
    path("watch/<slug:course_slug>/", watch_video, name="watch"),
    path("update-progress/<int:video_id>/", update_watch_progress, name="update_progress"),
    
    # My Enrollments
    path("my-enrollments/", my_enrollments, name="my_enrollments"),
    
    # Profile & Settings
    path("profile/", enroller_profile, name="profile"),
    
    # Reviews
    path("add-review/<int:enrollment_id>/", add_review, name="add_review"),
    
    # Index
    path("", index, name="index"),
]
