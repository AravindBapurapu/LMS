from django.db import models
from django.conf import settings
from adminstrator.models import CourseContent, CourseMedia
from accounts.models import Enrollment


class EnrollerProfile(models.Model):
    """Profile for Course Enroller users"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='enroller_profile'
    )
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='enroller/avatars/', 
        default='avatars/default.png'
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Enroller Profile: {self.user.username}"
    
    def get_enrolled_courses_count(self):
        """Get total enrolled courses"""
        return Enrollment.objects.filter(
            user=self.user, 
            is_paid=True
        ).count()
    
    def get_total_spent(self):
        """Get total amount spent on courses"""
        enrollments = Enrollment.objects.filter(
            user=self.user, 
            is_paid=True
        ).select_related('course')
        
        total = sum(e.course.price for e in enrollments)
        return total


class PaymentMethod(models.Model):
    """Store payment methods for enrollers"""
    PAYMENT_TYPE_CHOICES = (
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet'),
        ('netbanking', 'Net Banking'),
    )
    
    enroller = models.OneToOneField(
        EnrollerProfile, 
        on_delete=models.CASCADE, 
        related_name='payment_method'
    )
    payment_type = models.CharField(
        max_length=20, 
        choices=PAYMENT_TYPE_CHOICES, 
        default='card'
    )
    card_number = models.CharField(max_length=20, blank=True, null=True)
    card_holder_name = models.CharField(max_length=100, blank=True, null=True)
    expiry_month = models.IntegerField(blank=True, null=True)
    expiry_year = models.IntegerField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.enroller.user.username}"


class EnrollmentPayment(models.Model):
    """Track payments for course enrollments"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    enrollment = models.OneToOneField(
        Enrollment, 
        on_delete=models.CASCADE, 
        related_name='payment'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    transaction_id = models.CharField(max_length=255, unique=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.enrollment}"
    
    class Meta:
        ordering = ['-created_at']


class VideoWatchHistory(models.Model):
    """Track video watch history for enrollers"""
    enrollment = models.ForeignKey(
        Enrollment, 
        on_delete=models.CASCADE, 
        related_name='watch_history'
    )
    video = models.ForeignKey(
        CourseMedia, 
        on_delete=models.CASCADE
    )
    watch_duration = models.IntegerField(default=0, help_text="Duration watched in seconds")
    total_duration = models.IntegerField(default=0, help_text="Total video duration in seconds")
    is_completed = models.BooleanField(default=False)
    last_watched_at = models.DateTimeField(auto_now=True)
    first_watched_at = models.DateTimeField(auto_now_add=True)
    watch_count = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ['enrollment', 'video']
        ordering = ['-last_watched_at']
    
    def __str__(self):
        return f"{self.enrollment.user.username} - {self.video.id}"
    
    def get_completion_percentage(self):
        """Get video completion percentage"""
        if self.total_duration == 0:
            return 0
        return min(100, int((self.watch_duration / self.total_duration) * 100))


class EnrollmentCertificate(models.Model):
    """Certificates earned by enrollers"""
    enrollment = models.OneToOneField(
        Enrollment, 
        on_delete=models.CASCADE, 
        related_name='certificate'
    )
    certificate_number = models.CharField(
        max_length=100, 
        unique=True
    )
    issued_date = models.DateTimeField(auto_now_add=True)
    is_downloaded = models.BooleanField(default=False)
    downloaded_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Certificate for {self.enrollment.user.username}"


class EnrollerReview(models.Model):
    """Reviews and ratings from enrollers"""
    enrollment = models.OneToOneField(
        Enrollment, 
        on_delete=models.CASCADE, 
        related_name='review'
    )
    rating = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        help_text="Rating out of 5"
    )
    review_text = models.TextField(blank=True)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['enrollment']
    
    def __str__(self):
        return f"Review by {self.enrollment.user.username} for {self.enrollment.course.title}"
