from django.contrib import admin
from .models import (
    FacultyProfile,
    FacultyCourse,
    CourseMaterial,
    FacultyGuideline,
    FacultyContact,
    FacultyNotification,
    FacultyApplication
)


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise', 'experience', 'is_approved', 'approved_on')
    search_fields = ('user__username', 'user__email', 'expertise')
    list_filter = ('is_approved', 'experience')
    readonly_fields = ('approved_on',)
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'is_approved')
        }),
        ('Professional Info', {
            'fields': ('expertise', 'experience', 'qualification')
        }),
        ('Contact', {
            'fields': ('phone',)
        }),
        ('Media/Bio', {
            'fields': ('bio',)
        }),
        ('Timestamps', {
            'fields': ('approved_on',),
            'classes': ('collapse',)
        }),
    )


@admin.register(FacultyCourse)
class FacultyCourseAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'course', 'get_students_count', 'assigned_on', 'is_active')
    search_fields = ('faculty__user__username', 'course__title')
    list_filter = ('assigned_on', 'is_active')
    readonly_fields = ('assigned_on',)
    
    def get_students_count(self, obj):
        return obj.course.get_enrollment_count() if hasattr(obj.course, 'get_enrollment_count') else '-'
    get_students_count.short_description = 'Students Enrolled'


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'faculty_course', 'material_type', 'uploaded_on')
    search_fields = ('title', 'faculty_course__course__title')
    list_filter = ('material_type', 'uploaded_on')
    readonly_fields = ('uploaded_on',)
    
    fieldsets = (
        ('Material Info', {
            'fields': ('faculty_course', 'title', 'material_type')
        }),
        ('Content', {
            'fields': ('description', 'file', 'link')
        }),
        ('Upload Info', {
            'fields': ('uploaded_on',),
            'classes': ('collapse',)
        }),
    )


@admin.register(FacultyGuideline)
class FacultyGuidelineAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_on', 'is_active')
    search_fields = ('title', 'description')
    list_filter = ('created_on', 'is_active')
    readonly_fields = ('created_on',)


@admin.register(FacultyContact)
class FacultyContactAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'email', 'phone', 'available_from', 'available_to')
    search_fields = ('faculty__user__username', 'email', 'phone')


@admin.register(FacultyNotification)
class FacultyNotificationAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'title', 'is_read', 'created_on')
    search_fields = ('faculty__user__username', 'title', 'message')
    list_filter = ('is_read', 'created_on')
    readonly_fields = ('created_on',)


@admin.register(FacultyApplication)
class FacultyApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'status', 'applied_on', 'updated_on')
    search_fields = ('user__username', 'user__email', 'name', 'qualification')
    list_filter = ('status', 'applied_on', 'updated_on')
    readonly_fields = ('applied_on', 'updated_on')
    
    fieldsets = (
        ('Applicant Info', {
            'fields': ('user', 'name', 'email', 'phone')
        }),
        ('Application Details', {
            'fields': ('qualification', 'experience', 'expertise', 'bio', 'document', 'resume', 'online_mode', 'terms_accepted')
        }),
        ('Review Status', {
            'fields': ('status',),
            'classes': ('collapse',)
        }),
        ('Submission Info', {
            'fields': ('applied_on', 'updated_on'),
            'classes': ('collapse',)
        }),
    )
