from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Super Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    # Common details
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Student specific details
    roll = models.CharField(max_length=5, blank=True, null=True)
    class_section = models.CharField(max_length=20, blank=True, null=True) # e.g. "Class 8-B"
    admission_session = models.CharField(max_length=10, blank=True, null=True) # e.g. "2024"
    blood_group = models.CharField(max_length=5, blank=True, null=True) # e.g. "O+"
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Teacher specific details
    designation = models.CharField(max_length=50, blank=True, null=True) # e.g. "English Teacher"
    joining_date = models.DateField(blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True) # e.g. "Languages"
    
    # Verification Documents Status
    nid_uploaded = models.BooleanField(default=True)
    hsc_uploaded = models.BooleanField(default=True)
    bed_uploaded = models.BooleanField(default=True)
    appointment_uploaded = models.BooleanField(default=True)
    photo_uploaded = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class SchoolClass(models.Model):
    name = models.CharField(max_length=20, unique=True) # e.g. "Class 8-B"

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g. "English", "Mathematics"

    def __str__(self):
        return self.name


class RoutineSlot(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='routine_slots')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'TEACHER'})
    period_name = models.CharField(max_length=10) # e.g. "1st", "2nd"
    time_slot = models.CharField(max_length=20) # e.g. "8:00–8:45"
    weekday = models.CharField(max_length=15) # e.g. "Sunday", "Monday"

    def __str__(self):
        return f"{self.school_class.name} - {self.weekday} - {self.period_name} Period ({self.subject.name})"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HOLIDAY', 'Holiday'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances', limit_choices_to={'profile__role': 'STUDENT'})
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    time = models.TimeField(blank=True, null=True)
    method = models.CharField(max_length=20, default='Biometric')

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"


class Homework(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='homeworks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    assign_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'TEACHER'})

    def __str__(self):
        return f"{self.school_class.name} - {self.title}"


class HomeworkSubmission(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('GRADED', 'Graded'),
    ]
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='homework_submissions', limit_choices_to={'profile__role': 'STUDENT'})
    content = models.TextField(blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SUBMITTED')
    marks = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True) # e.g. 18.0 / 20.0
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('homework', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.homework.title} ({self.status})"


class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades', limit_choices_to={'profile__role': 'STUDENT'})
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_term = models.CharField(max_length=50, default='Mid-term 2026')
    mcq_marks = models.IntegerField(default=0)
    written_marks = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    letter_grade = models.CharField(max_length=5, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        self.total_marks = self.mcq_marks + self.written_marks
        # Auto calculate grades
        if self.total_marks >= 80:
            self.letter_grade = 'A+'
            self.grade_point = 5.00
        elif self.total_marks >= 70:
            self.letter_grade = 'A'
            self.grade_point = 4.00
        elif self.total_marks >= 60:
            self.letter_grade = 'A-'
            self.grade_point = 3.50
        elif self.total_marks >= 50:
            self.letter_grade = 'B'
            self.grade_point = 3.00
        elif self.total_marks >= 40:
            self.letter_grade = 'C'
            self.grade_point = 2.00
        elif self.total_marks >= 33:
            self.letter_grade = 'D'
            self.grade_point = 1.00
        else:
            self.letter_grade = 'F'
            self.grade_point = 0.00
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} ({self.letter_grade})"


class Notice(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
        ('INFO', 'Info'),
    ]
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='INFO')
    target = models.CharField(max_length=50, default='All') # e.g. "All Students", "All Parents", "Teachers"
    publish_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username} ({self.timestamp})"


class FeeInvoice(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partial'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fee_invoices', limit_choices_to={'profile__role': 'STUDENT'})
    invoice_no = models.CharField(max_length=30, unique=True)
    billing_month = models.CharField(max_length=20) # e.g. "June 2026"
    item_name = models.CharField(max_length=100, default='Tuition Fee')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='UNPAID')
    transaction_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.billing_month} - {self.status}"


class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_applications', limit_choices_to={'profile__role': 'TEACHER'})
    leave_type = models.CharField(max_length=20) # e.g. "Casual Leave", "Sick Leave"
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.teacher.username} - {self.leave_type} ({self.status})"


class Expense(models.Model):
    category = models.CharField(max_length=50)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    voucher_no = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"{self.category} - {self.amount} ({self.voucher_no})"
