from django.urls import path
# from .views import (
#     adminstrator,
#     enoll,
#     save_courses,
#     delete_course,
#     get_courses
# )
from .views import *
from accounts.views import *
from student.views import *

app_name = "adminstrator"

urlpatterns = [
    path("dashboard/", adminstrator, name="dashboard"),
    path("enroll/", enoll, name="enroll"),
    # html pages urls
    path('manage-course/', manage_course, name='manage_course'),
    path('manage-student/', manage_student, name='manage_student'),
    path('manage-faculty/', manage_faculty, name='manage_faculty'),
    path('report-analysis/', report_analysis, name='report_analysis'),

    # 🔥 API ROUTES (THIS WAS MISSING)
    path("save-courses/", save_courses, name="save_courses"),
    path("delete-course/<int:pk>/", delete_course, name="delete_course"),
    path("get-courses/", get_courses, name="get_courses"),

    # urls
    path("enroll/<int:course_id>/", enroll_course, name="enroll_course"),
    path("payment/<int:course_id>/", payment_page, name="payment_page"),
    path("fake-payment/<int:course_id>/", fake_payment_gateway, name="fake_payment"),
    path("verify-payment/<int:course_id>/", verify_payment, name="verify_payment"),
    

    # path("payment-success/<int:course_id>/", payment_success, name="payment_success"),
    path("process-payment/<int:course_id>/", process_payment, name="process_payment"),
    # path("all_courses/", courses, name="allCourses"),
    # path("courses/<int:course_id>/", course_videos, name="course_videos"),



    path("faculty_manage/", manage_faculty, name="faculty_manage"),

    path("approve-faculty/<int:pk>/", approve_faculty, name="approve_faculty"),
    path("reject-faculty/<int:pk>/", reject_faculty, name="reject_faculty"),

]
