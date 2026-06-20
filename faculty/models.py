from django.db import models
from django.conf import settings
from adminstrator.models import CourseContent
from django.contrib.auth.models import User  # Add this line

class Form_faculty(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField( unique=True,null=True, blank=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class FacultyApplication(models.Model):
    STATUS_CHOICES = (
        ('under_process', 'Under Process'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_applications')
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, default='temp@example.com')    
    phone = models.CharField(max_length=15, null=True, blank=True)  # Made nullable
    experience = models.IntegerField(help_text="Years of experience")
    qualification = models.CharField(max_length=200)
    expertise = models.CharField(max_length=200, help_text="Area of expertise", null=True, blank=True)
    tech = models.CharField(
        max_length=200,
        help_text="Legacy technology field for compatibility",
        null=True,
        blank=True,
        default='',
        db_column='tech'
    )
    bio = models.TextField(max_length=500, help_text="Short professional bio", blank=True, default='')
    
    document = models.FileField(upload_to='faculty/documents/', help_text="Upload your certificates")
    resume = models.FileField(upload_to='faculty/resumes/', help_text="Upload your resume")
    
    online_mode = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='under_process')
    applied_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    

    
class FacultyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile')
    phone = models.CharField(max_length=15, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    expertise = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    experience = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    approved_on = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

class FacultyCourse(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name='courses')
    course = models.ForeignKey(CourseContent, on_delete=models.CASCADE)
    assigned_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['faculty', 'course']
    
    def __str__(self):
        return f"{self.faculty.user.username} - {self.course.title}"

class CourseMaterial(models.Model):
    MATERIAL_TYPES = (
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('link', 'External Link'),
    )
    
    faculty_course = models.ForeignKey(FacultyCourse, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    file = models.FileField(upload_to='faculty/materials/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class FacultyGuideline(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_on']
    
    def __str__(self):
        return self.title

class FacultyContact(models.Model):
    faculty = models.OneToOneField(FacultyProfile, on_delete=models.CASCADE, related_name='contact_info')
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    alternative_phone = models.CharField(max_length=15, blank=True)
    office_address = models.TextField(blank=True)
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Contact info for {self.faculty.user.username}"

class FacultyNotification(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_on']
    
    def __str__(self):
        return self.title