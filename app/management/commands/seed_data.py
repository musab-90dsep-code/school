import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import (
    Profile, SchoolClass, Subject, RoutineSlot, Attendance, 
    Homework, HomeworkSubmission, Grade, Notice, Message, 
    FeeInvoice, LeaveApplication, Expense
)

class Command(BaseCommand):
    help = 'Seeds the database with mockup data for admin, teacher, and student portals.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing existing database records...")
        HomeworkSubmission.objects.all().delete()
        Homework.objects.all().delete()
        Attendance.objects.all().delete()
        RoutineSlot.objects.all().delete()
        Grade.objects.all().delete()
        Notice.objects.all().delete()
        Message.objects.all().delete()
        FeeInvoice.objects.all().delete()
        LeaveApplication.objects.all().delete()
        Expense.objects.all().delete()
        Profile.objects.all().delete()
        SchoolClass.objects.all().delete()
        Subject.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("Creating academic classes...")
        c8b = SchoolClass.objects.create(name="Class 8-B")
        c7a = SchoolClass.objects.create(name="Class 7-A")
        c9a = SchoolClass.objects.create(name="Class 9-A")
        c10a = SchoolClass.objects.create(name="Class 10-A")

        self.stdout.write("Creating subjects...")
        english = Subject.objects.create(name="English")
        math = Subject.objects.create(name="Mathematics")
        science = Subject.objects.create(name="General Science")
        bangla = Subject.objects.create(name="Bangla")
        religion = Subject.objects.create(name="Religion")
        ict = Subject.objects.create(name="ICT")

        self.stdout.write("Creating user accounts...")
        # 1. Admin
        admin_user = User.objects.create_user(username="admin", password="admin123", first_name="Super", last_name="Admin")
        Profile.objects.create(user=admin_user, role="ADMIN", phone="01711111111")

        # 2. Teacher (Fatema Khatun)
        teacher_user = User.objects.create_user(username="fatema", password="teacher123", first_name="Fatema", last_name="Khatun", email="fatema@school.edu.bd")
        teacher_prof = Profile.objects.create(
            user=teacher_user, role="TEACHER", phone="01722222222",
            designation="Senior English Teacher", department="Languages",
            joining_date=datetime.date(2021, 3, 15)
        )

        # Other mock teachers (just users for routine mapping)
        md_karim = User.objects.create_user(username="karim", password="teacher123", first_name="Md. Karim", last_name="Hossain")
        Profile.objects.create(user=md_karim, role="TEACHER", designation="Math Teacher", department="Mathematics")

        rahim_u = User.objects.create_user(username="rahim", password="teacher123", first_name="Rahim", last_name="Uddin")
        Profile.objects.create(user=rahim_u, role="TEACHER", designation="Head Teacher", department="Sciences")

        nasrin_a = User.objects.create_user(username="nasrin", password="teacher123", first_name="Nasrin", last_name="Akter")
        Profile.objects.create(user=nasrin_a, role="TEACHER", designation="Bangla Teacher", department="Languages")

        # 3. Student (Rahima Begum)
        student_user = User.objects.create_user(username="rahima", password="student123", first_name="Rahima", last_name="Begum", email="rahima@school.edu.bd")
        student_prof = Profile.objects.create(
            user=student_user, role="STUDENT", phone="01733333333",
            roll="01", class_section="Class 8-B", admission_session="2024",
            blood_group="O+", guardian_name="Karim Ali"
        )

        # Other students in Class 8-B
        imran_user = User.objects.create_user(username="imran", password="student123", first_name="Imran", last_name="Hossain")
        Profile.objects.create(user=imran_user, role="STUDENT", roll="02", class_section="Class 8-B", guardian_name="Rina Khatun")

        sadia_user = User.objects.create_user(username="sadia", password="student123", first_name="Sadia", last_name="Islam")
        Profile.objects.create(user=sadia_user, role="STUDENT", roll="03", class_section="Class 8-B", guardian_name="Jalal Uddin")

        nabil_user = User.objects.create_user(username="nabil", password="student123", first_name="Nabil", last_name="Ahmed")
        Profile.objects.create(user=nabil_user, role="STUDENT", roll="04", class_section="Class 8-B", guardian_name="Farida Begum")

        self.stdout.write("Creating weekly class routine...")
        # Routine slots for Class 8-B
        RoutineSlot.objects.create(school_class=c8b, subject=math, teacher=md_karim, period_name="1st", time_slot="8:00–8:45", weekday="Sunday")
        RoutineSlot.objects.create(school_class=c8b, subject=english, teacher=teacher_user, period_name="2nd", time_slot="8:45–9:30", weekday="Sunday")
        RoutineSlot.objects.create(school_class=c8b, subject=science, teacher=rahim_u, period_name="3rd", time_slot="9:45–10:30", weekday="Sunday")
        RoutineSlot.objects.create(school_class=c8b, subject=bangla, teacher=nasrin_a, period_name="4th", time_slot="10:30–11:15", weekday="Sunday")
        
        RoutineSlot.objects.create(school_class=c8b, subject=english, teacher=teacher_user, period_name="1st", time_slot="8:00–8:45", weekday="Monday")
        RoutineSlot.objects.create(school_class=c8b, subject=math, teacher=md_karim, period_name="3rd", time_slot="9:45–10:30", weekday="Tuesday")
        RoutineSlot.objects.create(school_class=c8b, subject=english, teacher=teacher_user, period_name="2nd", time_slot="8:45–9:30", weekday="Wednesday")
        RoutineSlot.objects.create(school_class=c8b, subject=science, teacher=rahim_u, period_name="1st", time_slot="8:00–8:45", weekday="Thursday")

        self.stdout.write("Creating attendance logs for Rahima Begum...")
        # Mocking 20 presents, 1 absent on June 10, 2 lates on June 8, June 14
        today = datetime.date.today()
        for i in range(1, 16):
            log_date = datetime.date(2026, 6, i)
            # Skip Fridays (assuming 5 & 12 are weekend)
            if log_date.weekday() in [4, 5]:
                Attendance.objects.create(student=student_user, date=log_date, status="HOLIDAY")
                continue
            
            if i == 10:
                Attendance.objects.create(student=student_user, date=log_date, status="ABSENT")
            elif i in [8, 14]:
                Attendance.objects.create(student=student_user, date=log_date, status="LATE", time=datetime.time(9, 18, 0))
            else:
                Attendance.objects.create(student=student_user, date=log_date, status="PRESENT", time=datetime.time(7, 54, 0))
                
        # Also seed today's attendance logs for Imran, Sadia
        Attendance.objects.create(student=imran_user, date=today, status="PRESENT", time=datetime.time(8, 45, 0))
        Attendance.objects.create(student=sadia_user, date=today, status="ABSENT")

        self.stdout.write("Creating notice board listings...")
        Notice.objects.create(title="Mid-term exam schedule published", content="All students can view their mid-term exam routines in the timetable panel.", priority="HIGH", target="All Students", created_by=admin_user)
        Notice.objects.create(title="Parent-Teacher Meeting regarding performance", content="Mandatory parent meeting scheduled on June 25th in Class 8 homeroom.", priority="MEDIUM", target="All Parents", created_by=admin_user)
        Notice.objects.create(title="Eid-ul-Adha holiday notice (June 18 to June 22)", content="The school will remain closed for Eid-ul-Adha.", priority="INFO", target="All", created_by=admin_user)

        self.stdout.write("Creating homework assignments...")
        hw1 = Homework.objects.create(school_class=c8b, subject=english, title='Essay Writing on "My Future Goal"', instructions="Write a 200 words composition on your future career goal.", due_date=datetime.date(2026, 6, 25), created_by=teacher_user)
        hw2 = Homework.objects.create(school_class=c8b, subject=math, title="Solve Exercise 4.2 (Sums 1 to 15)", instructions="Upload a photo or submit responses for Exercise 4.2 equations.", due_date=datetime.date(2026, 6, 12), created_by=md_karim)
        hw3 = Homework.objects.create(school_class=c8b, subject=bangla, title='Composition on "Borsha Kal in Bangladesh"', instructions="Write a short paragraph.", due_date=datetime.date(2026, 6, 10), created_by=nasrin_a)

        self.stdout.write("Submitting homework details...")
        # Rahima submits Math homework
        HomeworkSubmission.objects.create(homework=hw2, student=student_user, content="Solved Equations 1-15: x=2, y=5, z=12...", status="GRADED", marks=10.0, feedback="Excellent work!")
        # Rahima submits Bangla homework
        HomeworkSubmission.objects.create(homework=hw3, student=student_user, content="Borshokal holo shororiture prothom...", status="GRADED", marks=9.0, feedback="Very creative writing!")
        # Imran submits Bangla homework
        HomeworkSubmission.objects.create(homework=hw3, student=imran_user, content="Bangladeshe borshakaal bohut shundor...", status="SUBMITTED")

        self.stdout.write("Creating student grades...")
        Grade.objects.create(student=student_user, subject=english, mcq_marks=28, written_marks=66) # MCQ 28 + written 66 = 94 -> A+
        Grade.objects.create(student=student_user, subject=math, mcq_marks=29, written_marks=68) # 97 -> A+
        Grade.objects.create(student=student_user, subject=science, mcq_marks=25, written_marks=62) # 87 -> A+
        Grade.objects.create(student=student_user, subject=bangla, mcq_marks=26, written_marks=61) # 87 -> A+
        Grade.objects.create(student=student_user, subject=religion, mcq_marks=29, written_marks=66) # 95 -> A+
        Grade.objects.create(student=student_user, subject=ict, mcq_marks=28, written_marks=68) # 96 -> A+

        self.stdout.write("Creating tuition fee invoices...")
        FeeInvoice.objects.create(student=student_user, invoice_no="INV-2026-06", billing_month="June 2026", amount=1500.00, due_date=datetime.date(2026, 6, 15), status="UNPAID")
        FeeInvoice.objects.create(student=student_user, invoice_no="INV-2026-05", billing_month="May 2026", amount=1500.00, due_date=datetime.date(2026, 5, 15), status="PAID", paid_date=datetime.date(2026, 5, 4), transaction_id="BK20260504-1025")
        FeeInvoice.objects.create(student=student_user, invoice_no="INV-2026-04", billing_month="April 2026", amount=1500.00, due_date=datetime.date(2026, 4, 15), status="PAID", paid_date=datetime.date(2026, 4, 12), transaction_id="BK20260412-4012")

        # Invoices for Imran Hossain
        FeeInvoice.objects.create(student=imran_user, invoice_no="INV-IMRAN-06", billing_month="June 2026", amount=1500.00, due_date=datetime.date(2026, 6, 15), status="UNPAID")

        self.stdout.write("Creating expenses data...")
        Expense.objects.create(category="Utilities", description="Electricity bill", amount=18500.00, date=datetime.date(2026, 6, 5), voucher_no="V-001")
        Expense.objects.create(category="Maintenance", description="Roof repair", amount=12000.00, date=datetime.date(2026, 6, 8), voucher_no="V-002")
        Expense.objects.create(category="Stationery", description="Office supplies", amount=4200.00, date=datetime.date(2026, 6, 10), voucher_no="V-003")

        self.stdout.write("Creating test messages...")
        Message.objects.create(sender=student_user, receiver=teacher_user, content="Absence reason জানতে চাইছেন — Karim Ali")
        Message.objects.create(sender=teacher_user, receiver=student_user, content="নিজে এসে পরীক্ষার মার্কস শিট দেখবে। তোমার ইংলিশ গ্রামারে কিছু উন্নতি দরকার।")

        self.stdout.write("Creating teacher leave applications...")
        LeaveApplication.objects.create(teacher=teacher_user, leave_type="Sick Leave", start_date=datetime.date(2026, 5, 5), end_date=datetime.date(2026, 5, 6), reason="Fever", status="APPROVED")
        LeaveApplication.objects.create(teacher=teacher_user, leave_type="Casual Leave", start_date=datetime.date(2026, 4, 18), end_date=datetime.date(2026, 4, 18), reason="Personal", status="APPROVED")

        self.stdout.write(self.style.SUCCESS("Successfully seeded the school database!"))
