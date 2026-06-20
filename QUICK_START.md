# QUICK START COMMANDS

## Prerequisites
Ensure you have Python 3.8+ and Django 4.0+ installed

---

## Step 1: Make Migrations
```bash
cd c:\Users\aravi.AA\Desktop\Internship\lms_project

# Create migrations for course_enroller app
python manage.py makemigrations course_enroller

# Make migrations for all changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

## Step 2: Create Test Data
```bash
python manage.py shell
```

Then run in shell:
```python
from accounts.models import Accounts
from course_enroller.models import EnrollerProfile
from faculty.models import FacultyProfile

# Create test course enroller
enroller = Accounts.objects.create_user(
    username='enroller1',
    email='enroller@test.com',
    password='Test@123',
    first_name='John',
    last_name='Doe',
    role='course_enroller'
)
EnrollerProfile.objects.create(user=enroller)
print(f"✅ Enroller created: {enroller.username}")

# Create test faculty
faculty = Accounts.objects.create_user(
    username='faculty1',
    email='faculty@test.com',
    password='Test@123',
    first_name='Jane',
    last_name='Smith',
    role='faculty'
)
FacultyProfile.objects.create(user=faculty)
print(f"✅ Faculty created: {faculty.username}")

# Create superuser
admin = Accounts.objects.create_superuser(
    username='admin',
    email='admin@test.com',
    password='Admin@123',
    role='administrator'
)
print(f"✅ Admin created: {admin.username}")

print("\n✅ All test users created!")
```

Exit shell: `exit()`

---

## Step 3: Create Sample Courses (Optional)

```bash
python manage.py shell
```

```python
from adminstrator.models import CourseContent

course = CourseContent.objects.create(
    title="Python for Beginners",
    description="Learn Python programming from scratch",
    price=499.00,
    video_links={"youtube": ["https://youtube.com/watch?v=video1"]}
)
print(f"✅ Course created: {course.title}")
```

---

## Step 4: Run Development Server
```bash
python manage.py runserver
```

Server will run on: `http://127.0.0.1:8000/`

---

## 🔗 IMPORTANT URLs

### Course Enroller URLs
```
http://127.0.0.1:8000/course-enroller/              → Index
http://127.0.0.1:8000/course-enroller/register/     → Register
http://127.0.0.1:8000/course-enroller/login/        → Login
http://127.0.0.1:8000/course-enroller/browse/       → Browse Courses
http://127.0.0.1:8000/course-enroller/dashboard/    → Dashboard
http://127.0.0.1:8000/course-enroller/profile/      → Profile
```

### Faculty URLs
```
http://127.0.0.1:8000/faculty/home/                 → Home
http://127.0.0.1:8000/faculty/dashboard/            → Dashboard
http://127.0.0.1:8000/faculty/my-courses/           → My Courses
http://127.0.0.1:8000/faculty/profile/              → Profile
```

### Admin URLs
```
http://127.0.0.1:8000/admin/                        → Django Admin
```

---

## 🧪 TESTING WORKFLOWS

### 1. Test Course Enroller Registration
1. Go to: http://127.0.0.1:8000/course-enroller/register/
2. Fill form with:
   - First Name: `John`
   - Last Name: `Smith`
   - Username: `johnsmith123`
   - Email: `john@example.com`
   - Password: `Test@123`
   - Confirm: `Test@123`
3. Click Register
4. Verify success message

### 2. Test Course Enroller Login
1. Go to: http://127.0.0.1:8000/course-enroller/login/
2. Use credentials:
   - Username: `enroller1` (from test data)
   - Password: `Test@123`
3. Click Login
4. Redirect to dashboard

### 3. Test Course Browse & Filter
1. Go to: http://127.0.0.1:8000/course-enroller/browse/
2. Use search: Type course name
3. Filter by price: Select range
4. Sort by: Newest/Price
5. Click "View Details" on course

### 4. Test Course Enrollment & Payment
1. On course detail page
2. Click "Enroll Now"
3. Select payment method (Card/UPI/Wallet)
4. Fill dummy card details
5. Click "Pay" button
6. Verify enrollment success

### 5. Test Video Watching
1. After enrollment, click "Continue Learning"
2. Select video from playlist
3. Play video
4. Click "Next Video" to navigate
5. Check progress bar updates

---

## 📊 ADMIN PANEL USAGE

1. Go to: http://127.0.0.1:8000/admin/
2. Login with admin credentials
3. Navigate to sections:
   - **Accounts → Accounts** - Manage users
   - **Course Enroller → Enroller Profile** - View enrollers
   - **Course Enroller → Enrollment Payment** - Track payments
   - **Faculty → Faculty Profile** - Manage faculty
   - **Adminstrator → Course Content** - Manage courses

---

## 🐛 COMMON ERRORS & FIXES

### Error: "No such table: course_enroller_enrollerprofile"
**Fix**: Run migrations
```bash
python manage.py migrate
```

### Error: "TemplateDoesNotExist"
**Fix**: Verify template path and check TEMPLATES setting in settings.py

### Error: "CSRF token missing"
**Fix**: Add `{% csrf_token %}` to all POST forms

### Error: "Anonymous user cannot access"
**Fix**: Add `@login_required` decorator to view

---

## 📁 DIRECTORY STRUCTURE AFTER SETUP

```
lms_project/
├── db.sqlite3                      # Database
├── manage.py                       # Django management
├── templates/
│   ├── course_enroller/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── browse_courses.html
│   │   ├── course_detail.html
│   │   ├── payment.html
│   │   ├── watch_video.html
│   │   ├── my_enrollments.html
│   │   ├── profile.html
│   │   ├── login.html
│   │   └── register.html
│   ├── faculty/
│   │   ├── faculty_base.html
│   │   └── dashboard.html
│   └── [Other templates]
├── media/
│   ├── avatars/
│   ├── enroller/avatars/
│   ├── faculty/documents/
│   ├── faculty/materials/
│   └── course_media/
├── course_enroller/
│   ├── models.py               ✅ Complete
│   ├── views.py                ✅ Complete
│   ├── forms.py                ✅ Complete
│   ├── urls.py                 ✅ Complete
│   └── admin.py                ⚠️ Needs registration
├── faculty/
│   ├── models.py               ✅ Complete
│   ├── views.py                ✅ Complete
│   ├── forms.py                ✅ Complete
│   ├── urls.py                 ✅ Complete
│   └── admin.py                ⚠️ May need updates
└── lms_project/
    ├── settings.py             ✅ Ready
    ├── urls.py                 ⚠️ Update needed
    └── wsgi.py
```

---

## ✅ FINAL CHECKLIST

- [ ] Run `python manage.py migrate`
- [ ] Create test users
- [ ] Create sample courses
- [ ] Register models in admin.py
- [ ] Test all URLs
- [ ] Test workflows (register → login → browse → enroll → pay → watch)
- [ ] Test faculty workflow
- [ ] Check database relationships in admin
- [ ] Verify media files upload correctly
- [ ] Test responsive design on mobile

---

## 🚀 NEXT STEPS FOR PRODUCTION

1. **Security**
   - Change DEBUG=False in settings.py
   - Update SECRET_KEY
   - Configure ALLOWED_HOSTS
   - Setup HTTPS

2. **Database**
   - Use PostgreSQL instead of SQLite
   - Setup backups
   - Configure replication

3. **Email**
   - Configure real SMTP server
   - Send welcome emails
   - Send payment receipts

4. **Payment**
   - Integrate Razorpay API (remove demo)
   - Add webhook handling
   - Implement refunds

5. **Performance**
   - Setup caching (Redis)
   - Use CDN for static files
   - Optimize database queries

6. **Monitoring**
   - Setup error tracking (Sentry)
   - Configure logging
   - Monitor uptime

---

**Version**: 1.0
**Last Updated**: May 22, 2024
**Status**: ✅ READY FOR TESTING & DEPLOYMENT
