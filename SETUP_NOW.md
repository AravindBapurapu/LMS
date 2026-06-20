# ✅ FINAL SETUP - RUN THESE COMMANDS IN ORDER

## **🟢 DO THIS NOW** (Copy & Paste into Terminal)

### **1. Navigate to Project**
```bash
cd c:\Users\aravi.AA\Desktop\Internship\lms_project
```

### **2. Run Migrations** 
```bash
python manage.py makemigrations course_enroller
python manage.py makemigrations faculty  
python manage.py migrate
```

**Expected output:**
```
Operations to perform:
  Apply all migrations...
Running migrations:
  Applying course_enroller.0001_initial... OK
  Applying faculty.0001_initial... OK
```

### **3. Create Admin User**
```bash
python manage.py createsuperuser
```

**Input when prompted:**
```
Username: admin
Email: admin@example.com
Password: Admin@123
Password (again): Admin@123
Superuser created successfully.
```

### **4. Create Test Users** 
```bash
python manage.py shell
```

Copy & paste this entire block:
```python
from accounts.models import Accounts
from course_enroller.models import EnrollerProfile
from faculty.models import FacultyProfile

# Create enroller
e = Accounts.objects.create_user(username='enroller1', email='e@test.com', password='Test@123', role='course_enroller')
EnrollerProfile.objects.create(user=e)

# Create faculty
f = Accounts.objects.create_user(username='faculty1', email='f@test.com', password='Test@123', role='faculty')
FacultyProfile.objects.create(user=f)

print("✅ Users created successfully!")
print("Enroller: enroller1 / Test@123")
print("Faculty: faculty1 / Test@123")
print("Admin: admin / Admin@123")
```

Exit: `exit()`

### **5. Start Server**
```bash
python manage.py runserver
```

---

## **🔗 TEST THESE URLS**

Copy & paste into browser while server is running:

### **Admin Panel**
```
http://127.0.0.1:8000/admin/
Login: admin / Admin@123
```

### **Course Enroller**
```
http://127.0.0.1:8000/course/
http://127.0.0.1:8000/course/login/
Login: enroller1 / Test@123
http://127.0.0.1:8000/course/dashboard/
http://127.0.0.1:8000/course/browse/
http://127.0.0.1:8000/course/profile/
```

### **Faculty**
```
http://127.0.0.1:8000/faculty/
http://127.0.0.1:8000/faculty/dashboard/
Login: faculty1 / Test@123
```

---

## **✅ VERIFICATION CHECKLIST**

Go to `http://127.0.0.1:8000/admin/` and check:

- [ ] Course Enroller Models appear:
  - Enroller Profile
  - Payment Method
  - Enrollment Payment
  - Video Watch History
  - Enrollment Certificate
  - Enroller Review

- [ ] Faculty Models appear:
  - Faculty Profile
  - Faculty Course
  - Course Material
  - Faculty Guideline
  - Faculty Contact
  - Faculty Notification
  - Faculty Application

- [ ] Test user created:
  - Click Accounts → Accounts
  - See admin, enroller1, faculty1

---

## **🎯 IF YOU GET "PAGE NOT FOUND" ERROR**

### **Check URLs are correct:**
- ❌ WRONG: `/course-enroller/`
- ✅ CORRECT: `/course/`

- ❌ WRONG: `/faculty-home/`
- ✅ CORRECT: `/faculty/`

### **Check migrations ran:**
```bash
python manage.py migrate --list
```

Look for checkmarks (✓) next to course_enroller and faculty migrations.

### **Check models in admin:**
```bash
python manage.py admin
```

Should show all course_enroller and faculty models registered.

---

## **📋 NEXT STEPS AFTER VERIFICATION**

1. ✅ Test enroller registration: `/course/register/`
2. ✅ Test enroller login: `/course/login/`
3. ✅ Test faculty dashboard
4. ✅ Create sample courses in admin
5. ✅ Create test enrollments
6. ✅ Test payment flow
7. ✅ Test video watching

---

## **🚀 PRODUCTION READY**

After verification, your app is **production-ready**! 

To deploy to server:
1. Change `DEBUG = False` in [settings.py](lms_project/settings.py)
2. Update `ALLOWED_HOSTS` with your domain
3. Setup Gunicorn + Nginx
4. Configure SSL certificate
5. Setup database backups
6. Configure email server

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for full guide.

---

**Status**: ✅ READY TO TEST
