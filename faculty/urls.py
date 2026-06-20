from django.urls import path
from .views import *

app_name = "faculty"

urlpatterns = [
    path("dashboard/", faculty_dashboard, name="dashboard"),
    path("home/", faculty_home, name="faculty_home"),
    path("apply/", apply_faculty, name="apply_faculty"),
    path("application-status/", application_status, name="application_status"),
    
    # Course management
    path("my-courses/", my_courses, name="my_courses"),
    path("course/<int:course_id>/", course_detail, name="course_detail"),
    
    # Materials
    path("add-material/<int:course_id>/", add_material, name="add_material"),
    path("edit-material/<int:material_id>/", edit_material, name="edit_material"),
    path("delete-material/<int:material_id>/", delete_material, name="delete_material"),
    
    # Records/Students
    path("add-records/", add_records, name="add_records"),
    path("course-students/<int:course_id>/", course_students, name="course_students"),
    
    # Guidelines
    path("guidelines/", guidelines, name="guidelines"),
    
    # Contact
    path("contact/", faculty_contact, name="faculty_contact"),
    path("update-contact/", update_contact, name="update_contact"),
    
    # Profile
    path("profile/", faculty_profile, name="faculty_profile"),
    path("update-profile/", update_faculty_profile, name="update_faculty_profile"),
    
    # Notifications
    path("notifications/", notifications, name="notifications"),
    path("get-notifications/", get_notifications, name="get_notifications"),
    path("mark-notification-read/<int:notification_id>/", mark_notification_read, name="mark_notification_read"),


    path("update-profile/", update_faculty_profile, name="update_faculty_profile"),
]