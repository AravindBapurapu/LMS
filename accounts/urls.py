from django.urls import path
from .views import *
from adminstrator.views import *


app_name = "accounts"

urlpatterns = [
    path("", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("send-otp/", send_otp, name="send_otp"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("enroll/<int:course_id>/", enroll_course, name="enroll_course"),
    path("payment/<int:course_id>/", payment_page, name="payment_page"),
    path('change-password/', change_password, name='change_password'),
    path('update-profile/', update_profile, name='update_profile')


    # path("payment-success/<int:course_id>/", payment_success, name="payment_success"),
]
