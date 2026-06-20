from django.db import models
from django.utils.text import slugify

class CourseContent(models.Model):
    thumbnail = models.ImageField(upload_to="images/", blank=True, null=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=None)  
    video_links = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
# creating a table for seperate video and image storage purpose
class CourseMedia(models.Model):
    course = models.ForeignKey(
        CourseContent,
        related_name="media",
        on_delete=models.CASCADE
    )
    video_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to="course_media/", blank=True, null=True)

    def __str__(self):
        return f"Media for {self.course.title}"

