import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
username = 'testfaculty3'
email = 'testfaculty3@example.com'
password = 'Test12345'
user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'role': 'student'})
user.set_password(password)
user.save()
client = Client()
print('login', client.login(username=username, password=password))
cert = SimpleUploadedFile('cert.pdf', b'%PDF-1.4 test', content_type='application/pdf')
resume = SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test', content_type='application/pdf')
response = client.post('/faculty/apply/', {
    'name': 'Test Faculty',
    'email': email,
    'phone': '1234567890',
    'experience': '5',
    'qualification': 'MSc',
    'expertise': 'Math',
    'bio': 'Teaching experience',
    'online_mode': 'on',
    'terms_accepted': 'on'
}, follow=True, HTTP_HOST='localhost', HTTP_X_REQUESTED_WITH='XMLHttpRequest', FILES={'document': cert, 'resume': resume})
print('status', response.status_code)
print('redirect_chain', response.redirect_chain)
print('content', response.content[:1000])
print('context', response.context)
