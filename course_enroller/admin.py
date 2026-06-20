from django.contrib import admin
from .models import (
    EnrollerProfile, 
    PaymentMethod, 
    EnrollmentPayment, 
    VideoWatchHistory, 
    EnrollmentCertificate, 
    EnrollerReview
)


@admin.register(EnrollerProfile)
class EnrollerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_joined', 'get_enrolled_courses')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('date_joined',)
    readonly_fields = ('date_joined', 'updated_at')
    
    def get_enrolled_courses(self, obj):
        return obj.get_enrolled_courses_count()
    get_enrolled_courses.short_description = 'Enrolled Courses'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('enroller', 'payment_type', 'is_default', 'is_verified')
    search_fields = ('enroller__user__username', 'card_holder_name')
    list_filter = ('payment_type', 'is_default', 'is_verified')
    readonly_fields = ('created_at',)


@admin.register(EnrollmentPayment)
class EnrollmentPaymentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'amount', 'status', 'transaction_id', 'paid_at')
    search_fields = ('enrollment__user__username', 'transaction_id', 'razorpay_order_id')
    list_filter = ('status', 'created_at')
    readonly_fields = ('transaction_id', 'created_at')
    
    fieldsets = (
        ('Enrollment Info', {
            'fields': ('enrollment', 'payment_method')
        }),
        ('Payment Details', {
            'fields': ('amount', 'status', 'transaction_id')
        }),
        ('Razorpay Integration', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('paid_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VideoWatchHistory)
class VideoWatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'video', 'get_progress', 'is_completed')
    search_fields = ('enrollment__user__username', 'video__course__title')
    list_filter = ('is_completed', 'first_watched_at')
    readonly_fields = ('first_watched_at', 'last_watched_at')
    
    def get_progress(self, obj):
        return f"{obj.get_completion_percentage():.0f}%"
    get_progress.short_description = 'Progress'


@admin.register(EnrollmentCertificate)
class EnrollmentCertificateAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'certificate_number', 'issued_date', 'is_downloaded')
    search_fields = ('enrollment__user__username', 'certificate_number')
    list_filter = ('issued_date', 'is_downloaded')
    readonly_fields = ('certificate_number', 'issued_date')
    
    def has_add_permission(self, request):
        return False


@admin.register(EnrollerReview)
class EnrollerReviewAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'rating', 'helpful_count', 'created_at')
    search_fields = ('enrollment__user__username', 'review_text')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
