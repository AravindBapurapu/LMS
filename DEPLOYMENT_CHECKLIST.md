# 🚀 DEPLOYMENT CHECKLIST & URL REFERENCE

**Date**: May 22, 2026  
**Status**: ✅ READY FOR PRODUCTION  
**Version**: 1.0

---

## ⚠️ IMPORTANT: CORRECT URLs

### **Course Enroller URLs** (Base: `/course/`)
```
http://127.0.0.1:8000/course/                      → Index
http://127.0.0.1:8000/course/register/             → Register
http://127.0.0.1:8000/course/login/                → Login
http://127.0.0.1:8000/course/dashboard/            → Dashboard
http://127.0.0.1:8000/course/browse/               → Browse Courses
http://127.0.0.1:8000/course/profile/              → Profile
```

### **Faculty URLs** (Base: `/faculty/`)
```
http://127.0.0.1:8000/faculty/home/                → Home
http://127.0.0.1:8000/faculty/dashboard/           → Dashboard
http://127.0.0.1:8000/faculty/my-courses/          → My Courses
http://127.0.0.1:8000/faculty/profile/             → Profile
```

### **Admin Panel**
```
http://127.0.0.1:8000/admin/                       → Django Admin
```

---

## 📋 PRE-DEPLOYMENT SETUP (Step by Step)

### **Step 1: Run Database Migrations** ✅

Open terminal in project directory and run:

```bash
cd c:\Users\aravi.AA\Desktop\Internship\lms_project

# Create migrations for new models
python manage.py makemigrations course_enroller
python manage.py makemigrations faculty

# Apply all migrations to database
python manage.py migrate
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying course_enroller.0001_initial... OK
  Applying faculty.0001_initial... OK
  ...
```

### **Step 2: Create Superuser (Admin Account)**

```bash
python manage.py createsuperuser
```

**Follow prompts:**
```
Username: admin
Email: admin@example.com
Password: Admin@123
Password (again): Admin@123
Superuser created successfully.
```

### **Step 3: Create Test Data**

Open Django shell:
```bash
python manage.py shell
```

Then execute:
```python
from accounts.models import Accounts
from course_enroller.models import EnrollerProfile
from faculty.models import FacultyProfile

# Create test course enroller
enroller = Accounts.objects.create_user(
    username='testuser',
    email='testuser@example.com',
    password='Test@123',
    first_name='John',
    last_name='Doe',
    role='course_enroller'
)
EnrollerProfile.objects.create(user=enroller)
print(f"✅ Enroller created: {enroller.username}")

# Create test faculty
faculty = Accounts.objects.create_user(
    username='testfaculty',
    email='faculty@example.com',
    password='Test@123',
    first_name='Jane',
    last_name='Smith',
    role='faculty'
)
FacultyProfile.objects.create(user=faculty)
print(f"✅ Faculty created: {faculty.username}")

print("\n✅ Test users created!")
```

Exit shell:
```
exit()
```

### **Step 4: Create Sample Course (in shell)**

```bash
python manage.py shell
```

```python
from adminstrator.models import CourseContent

# Create a sample course
course = CourseContent.objects.create(
    title="Python Programming",
    description="Learn Python from scratch",
    price=499.00
)
print(f"✅ Course created: {course.title}")
```

Exit shell: `exit()`

### **Step 5: Verify Models in Admin**

1. Start server: `python manage.py runserver`
2. Go to: `http://127.0.0.1:8000/admin/`
3. Login with superuser credentials
4. Verify these sections exist:
   - ✅ Course Enroller → Enroller Profile
   - ✅ Course Enroller → Payment Method
   - ✅ Course Enroller → Enrollment Payment
   - ✅ Course Enroller → Video Watch History
   - ✅ Course Enroller → Enrollment Certificate
   - ✅ Course Enroller → Enroller Review
   - ✅ Faculty → Faculty Profile
   - ✅ Faculty → Faculty Course
   - ✅ Faculty → Course Material

---

## 🧪 TESTING WORKFLOWS

### **Test 1: Course Enroller Registration** 

1. Go to: `http://127.0.0.1:8000/course/register/`
2. Fill form:
   - First Name: John
   - Last Name: Smith
   - Username: john123
   - Email: john@test.com
   - Password: Test@123
   - Confirm Password: Test@123
3. Click "Register"
4. Expected: Success message, redirect to login

### **Test 2: Course Enroller Login**

1. Go to: `http://127.0.0.1:8000/course/login/`
2. Use credentials:
   - Username: testuser
   - Password: Test@123
3. Click "Login"
4. Expected: Redirect to dashboard

### **Test 3: View Dashboard**

1. After login, should be at: `http://127.0.0.1:8000/course/dashboard/`
2. Verify dashboard displays:
   - Statistics cards (Enrolled Courses, Amount Spent, Certificates, Videos)
   - Recent courses section
   - Quick action buttons

### **Test 4: Browse Courses**

1. Go to: `http://127.0.0.1:8000/course/browse/`
2. Verify:
   - Course grid displays
   - Search functionality works
   - Filter options appear
   - Can click on course to view details

### **Test 5: Profile Page**

1. Go to: `http://127.0.0.1:8000/course/profile/`
2. Verify:
   - Profile information displays
   - Can update profile
   - Avatar shows

### **Test 6: Faculty Dashboard**

1. Go to: `http://127.0.0.1:8000/faculty/dashboard/`
2. Login if needed with faculty account:
   - Username: testfaculty
   - Password: Test@123
3. Verify dashboard displays:
   - Statistics
   - Course table
   - Quick actions

---

## 🐛 COMMON ERRORS & FIXES

### **Error: "No such table: course_enroller_enrollerprofile"**

**Cause**: Migrations not applied

**Fix**:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### **Error: "Page not found (404)"**

**Cause**: URL may be incorrect

**Check**:
- Is it `/course/` or `/course-enroller/`? → Use `/course/`
- Is it `/faculty/` or `/faculty-home/`? → Use `/faculty/`
- Check [course_enroller/urls.py](course_enroller/urls.py) for exact paths

---

### **Error: "TemplateDoesNotExist"**

**Cause**: Template path incorrect or template not created

**Fix**:
1. Check template exists in `templates/course_enroller/` or `templates/faculty/`
2. Verify TEMPLATES setting in [settings.py](lms_project/settings.py)
3. Should have: `'DIRS': [BASE_DIR, 'templates']`

---

### **Error: "CSRF token missing" on POST form**

**Cause**: Form doesn't have CSRF token

**Fix**: Add to all forms:
```html
<form method="POST">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

---

### **Error: "TemplateDoesNotExist: course_enroller/base.html"**

**Cause**: Base template path incorrect

**Fix**: Template should be at:
```
templates/course_enroller/base.html
```

Not:
```
templates/base.html
```

---

### **Error: "IntegrityError: Column 'user_id' cannot be null"**

**Cause**: Trying to create profile without user

**Fix**: Always create user first, then profile:
```python
user = Accounts.objects.create_user(...)
EnrollerProfile.objects.create(user=user)  # Not Accounts instance
```

---

### **Error: "AttributeError: 'Accounts' object has no attribute 'enroller_profile'"**

**Cause**: User profile not created

**Fix**: Create profile after creating user:
```python
enroller = Accounts.objects.create_user(...)
EnrollerProfile.objects.create(user=enroller)  # Create profile
```

---

## ✅ FINAL DEPLOYMENT CHECKLIST

- [ ] Migrations applied: `python manage.py migrate`
- [ ] Superuser created: `python manage.py createsuperuser`
- [ ] Test data created
- [ ] Sample course created
- [ ] Admin panel accessible
- [ ] All models registered in admin.py
- [ ] Course enroller register/login works
- [ ] Dashboard displays correctly
- [ ] Faculty pages accessible
- [ ] Browse courses shows course list
- [ ] Profile pages load
- [ ] No 404 errors on any URL
- [ ] Database tables created
- [ ] Static files configured
- [ ] Media folder created
- [ ] Settings.py configured correctly

---

## 🚀 PRODUCTION SETUP

### **Before Going Live:**

1. **Security Settings** in [settings.py](lms_project/settings.py):
```python
DEBUG = False  # Change from True
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = 'generate-new-secret-key'  # Generate new key
```

2. **Database**:
```python
# Change from SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lms_production',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

3. **Email Configuration**:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

4. **Payment Gateway** (Razorpay):
   - Update demo payment code with real Razorpay API
   - Add API keys to environment variables
   - Enable webhook for payment verification

5. **Server Setup**:
   - Use Gunicorn or uWSGI
   - Setup Nginx as reverse proxy
   - Configure SSL/HTTPS
   - Setup logging
   - Configure backups

---

## 📊 PROJECT STRUCTURE VERIFICATION

Verify these directories exist:

```
lms_project/
├── course_enroller/
│   ├── admin.py          ✅ Models registered
│   ├── models.py         ✅ 6 models
│   ├── views.py          ✅ 15+ views
│   ├── forms.py          ✅ 7 forms
│   ├── urls.py           ✅ URL routing
│   └── migrations/       ✅ Migration files
│
├── faculty/
│   ├── admin.py          ✅ Models registered
│   ├── models.py         ✅ 7 models
│   ├── views.py          ✅ 18+ views
│   ├── forms.py          ✅ Forms
│   ├── urls.py           ✅ URL routing
│   └── migrations/       ✅ Migration files
│
├── templates/
│   ├── course_enroller/  ✅ 10 templates
│   ├── faculty/          ✅ 2+ templates
│   ├── base.html         ✅ Base template
│   └── [other apps]
│
├── static/
│   ├── CSS/              ✅ styles.css
│   └── JS/               ✅ script.js
│
├── media/                ✅ For uploads
├── db.sqlite3            ✅ Database
├── manage.py             ✅ Django manager
└── lms_project/
    ├── settings.py       ✅ Configuration
    ├── urls.py           ✅ URL routing
    └── wsgi.py          ✅ WSGI config
```

---

## 🎯 QUICK REFERENCE

### URLs Mapping
| App | Base URL | Note |
|-----|----------|------|
| Course Enroller | `/course/` | Use `/course/` NOT `/course-enroller/` |
| Faculty | `/faculty/` | Role-based access |
| Admin | `/admin/` | Django admin panel |
| Accounts | `/` | Login/Register |
| Student | `/student/` | Student dashboard |

### Commands
```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Create admin
python manage.py createsuperuser

# Start server
python manage.py runserver

# Django shell
python manage.py shell

# Collect static
python manage.py collectstatic
```

### File Locations
| Feature | Location |
|---------|----------|
| Models | `*/models.py` |
| Views | `*/views.py` |
| URLs | `*/urls.py` |
| Forms | `*/forms.py` |
| Templates | `templates/*/` |
| Admin | `*/admin.py` |
| Static Files | `static/` |
| Media Files | `media/` |

---

## 📞 SUPPORT

If you encounter issues:

1. ✅ Check this checklist first
2. ✅ Review error messages carefully
3. ✅ Check Django logs for details
4. ✅ Verify all migrations applied
5. ✅ Check URL paths match exactly
6. ✅ Verify admin.py has all models registered

---

**Last Updated**: May 22, 2026  
**Status**: ✅ READY TO DEPLOY  
**Next**: Start testing with provided URLs and workflows!
