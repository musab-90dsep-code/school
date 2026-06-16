import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import Sum
from app.models import (
    Profile, SchoolClass, Subject, RoutineSlot, Attendance, 
    Homework, HomeworkSubmission, Grade, Notice, Message, 
    FeeInvoice, LeaveApplication, Expense
)

def home_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Auto-create profile for superuser if it doesn't exist
    if not hasattr(request.user, 'profile'):
        if request.user.is_superuser:
            Profile.objects.create(user=request.user, role='ADMIN')
        else:
            return redirect('login')
            
    role = request.user.profile.role
    if role == 'ADMIN':
        return redirect('admin_panel')
    elif role == 'TEACHER':
        return redirect('teacher_portal')
    elif role == 'STUDENT':
        return redirect('student_portal')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home_redirect')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home_redirect')
        else:
            return render(request, 'app/login.html', {'error': 'Invalid username or password'})
    return render(request, 'app/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def admin_panel_view(request):
    if not hasattr(request.user, 'profile'):
        if request.user.is_superuser:
            Profile.objects.create(user=request.user, role='ADMIN')
        else:
            return redirect('home_redirect')
            
    if request.user.profile.role != 'ADMIN':
        return redirect('home_redirect')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_student':
            # Create user and profile
            username = request.POST.get('username')
            passw = request.POST.get('password')
            first = request.POST.get('first_name')
            last = request.POST.get('last_name')
            class_sec = request.POST.get('class_section')
            roll = request.POST.get('roll')
            guardian = request.POST.get('guardian')
            phone = request.POST.get('phone')

            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=passw, first_name=first, last_name=last)
                Profile.objects.create(
                    user=user, role='STUDENT', roll=roll, class_section=class_sec,
                    guardian_name=guardian, phone=phone, admission_session='2026'
                )
        elif action == 'create_notice':
            title = request.POST.get('title')
            content = request.POST.get('content')
            priority = request.POST.get('priority')
            target = request.POST.get('target')
            Notice.objects.create(title=title, content=content, priority=priority, target=target, created_by=request.user)
        elif action == 'approve_leave':
            leave_id = request.POST.get('leave_id')
            LeaveApplication.objects.filter(id=leave_id).update(status='APPROVED')
        elif action == 'reject_leave':
            leave_id = request.POST.get('leave_id')
            LeaveApplication.objects.filter(id=leave_id).update(status='REJECTED')

        return redirect('admin_panel')

    # Get Dashboard Statistics
    students_count = Profile.objects.filter(role='STUDENT').count()
    teachers_count = Profile.objects.filter(role='TEACHER').count()
    
    collected_fees = FeeInvoice.objects.filter(status='PAID').aggregate(Sum('amount'))['amount__sum'] or 0.00
    outstanding_fees = FeeInvoice.objects.filter(status='UNPAID').aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    paid_invoice_count = FeeInvoice.objects.filter(status='PAID').count()
    unpaid_invoice_count = FeeInvoice.objects.filter(status='UNPAID').count()

    students = Profile.objects.filter(role='STUDENT')
    teachers = Profile.objects.filter(role='TEACHER')
    notices = Notice.objects.all().order_by('-publish_date')
    leaves = LeaveApplication.objects.all().order_by('-id')
    invoices = FeeInvoice.objects.all().order_by('-due_date')
    routine_slots = RoutineSlot.objects.all()
    grades = Grade.objects.all()
    expenses = Expense.objects.all()
    
    # Simple attendance metric
    attend_present = Attendance.objects.filter(status='PRESENT').count()
    attend_absent = Attendance.objects.filter(status='ABSENT').count()
    attend_late = Attendance.objects.filter(status='LATE').count()
    total_attend = attend_present + attend_absent + attend_late
    attendance_pct = round((attend_present / total_attend * 100), 1) if total_attend > 0 else 91.0
    attendances = Attendance.objects.all().order_by('-date')

    context = {
        'students_count': students_count,
        'teachers_count': teachers_count,
        'collected_fees': collected_fees,
        'outstanding_fees': outstanding_fees,
        'paid_invoice_count': paid_invoice_count,
        'unpaid_invoice_count': unpaid_invoice_count,
        'students': students,
        'teachers': teachers,
        'notices': notices,
        'leaves': leaves,
        'invoices': invoices,
        'routine_slots': routine_slots,
        'grades': grades,
        'expenses': expenses,
        'attendance_pct': attendance_pct,
        'attend_present': attend_present,
        'attend_absent': attend_absent,
        'attend_late': attend_late,
        'attendances': attendances
    }
    return render(request, 'app/admin_panel.html', context)


@login_required
def teacher_portal_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'TEACHER':
        return redirect('home_redirect')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'assign_homework':
            class_name = request.POST.get('school_class')
            subj_name = request.POST.get('subject')
            title = request.POST.get('title')
            due_date = request.POST.get('due_date')

            s_class = SchoolClass.objects.get(name=class_name)
            subject = Subject.objects.get(name=subj_name)
            Homework.objects.create(
                school_class=s_class, subject=subject, title=title, 
                due_date=due_date, created_by=request.user
            )
        elif action == 'grade_homework':
            sub_id = request.POST.get('submission_id')
            marks = request.POST.get('marks')
            feedback = request.POST.get('feedback')
            HomeworkSubmission.objects.filter(id=sub_id).update(marks=marks, feedback=feedback, status='GRADED')

        return redirect('teacher_portal')

    # Get Teacher dashboard details
    teacher_profile = request.user.profile
    routine_slots = RoutineSlot.objects.filter(teacher=request.user)
    class_students = Profile.objects.filter(role='STUDENT', class_section='Class 8-B')
    homeworks = Homework.objects.filter(created_by=request.user).order_by('-id')
    hw_submissions = HomeworkSubmission.objects.filter(homework__created_by=request.user, status='SUBMITTED')
    
    student_grades = Grade.objects.filter(subject__name='English')
    chat_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    notices = Notice.objects.all().order_by('-publish_date')
    teacher_leaves = LeaveApplication.objects.filter(teacher=request.user).order_by('-id')
    pending_hw_count = HomeworkSubmission.objects.filter(homework__created_by=request.user, status='SUBMITTED').count()

    context = {
        'teacher_profile': teacher_profile,
        'routine_slots': routine_slots,
        'class_students': class_students,
        'homeworks': homeworks,
        'hw_submissions': hw_submissions,
        'student_grades': student_grades,
        'chat_messages': chat_messages,
        'notices': notices,
        'teacher_leaves': teacher_leaves,
        'pending_hw_count': pending_hw_count
    }
    return render(request, 'app/teacher_portal.html', context)


@login_required
def student_portal_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'STUDENT':
        return redirect('home_redirect')

    student_profile = request.user.profile
    routine_slots = RoutineSlot.objects.filter(school_class__name=student_profile.class_section)
    
    # Fetch active homeworks that have not been submitted by this student
    submitted_hw_ids = HomeworkSubmission.objects.filter(student=request.user).values_list('homework_id', flat=True)
    pending_homeworks = Homework.objects.filter(school_class__name=student_profile.class_section).exclude(id__in=submitted_hw_ids)
    
    grades = Grade.objects.filter(student=request.user)
    attendances = Attendance.objects.filter(student=request.user).order_by('-date')
    invoices = FeeInvoice.objects.filter(student=request.user).order_by('-due_date')
    chat_messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    notices = Notice.objects.all().order_by('-publish_date')
    
    outstanding_fees = FeeInvoice.objects.filter(student=request.user, status='UNPAID').aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    total_days = 22
    present_days = attendances.filter(status='PRESENT').count()
    attendance_pct = round((present_days / total_days * 100), 1) if present_days > 0 else 96.8
    teachers = Profile.objects.filter(role='TEACHER')

    context = {
        'student_profile': student_profile,
        'routine_slots': routine_slots,
        'pending_homeworks': pending_homeworks,
        'grades': grades,
        'attendances': attendances,
        'invoices': invoices,
        'chat_messages': chat_messages,
        'notices': notices,
        'outstanding_fees': outstanding_fees,
        'attendance_pct': attendance_pct,
        'teachers': teachers
    }
    return render(request, 'app/student_portal.html', context)


# --- AJAX POST API Views ---

@login_required
def submit_homework_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        hw_id = data.get('homework_id')
        content = data.get('content')
        homework = Homework.objects.get(id=hw_id)
        
        HomeworkSubmission.objects.update_or_create(
            homework=homework, student=request.user,
            defaults={'content': content, 'status': 'SUBMITTED'}
        )
        return JsonResponse({'message': 'Homework assignment submitted successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def mark_attendance_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        records = data.get('records', [])
        for r in records:
            stud_id = r.get('student_id')
            status = r.get('status')
            student = User.objects.get(id=stud_id)
            Attendance.objects.update_or_create(
                student=student, date=now().date(),
                defaults={'status': status, 'time': now().time(), 'method': 'Manual override'}
            )
        return JsonResponse({'message': 'Attendance marked successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def save_marks_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subject_name = data.get('subject')
        records = data.get('records', [])
        subject = Subject.objects.get(name=subject_name)
        
        for r in records:
            stud_id = r.get('student_id')
            mcq = int(r.get('mcq', 0))
            written = int(r.get('written', 0))
            student = User.objects.get(id=stud_id)
            
            Grade.objects.update_or_create(
                student=student, subject=subject, exam_term='Mid-term 2026',
                defaults={'mcq_marks': mcq, 'written_marks': written}
            )
        return JsonResponse({'message': 'Grades processed and stored successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def pay_fee_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        inv_id = data.get('invoice_id')
        trx_id = data.get('trx_id')
        
        FeeInvoice.objects.filter(id=inv_id).update(
            status='PAID', paid_date=now().date(), transaction_id=trx_id
        )
        return JsonResponse({'message': 'Tuition Fee paid successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def send_message_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        receiver = User.objects.get(id=receiver_id)
        
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return JsonResponse({'message': 'Message sent successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def apply_leave_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        leave_type = data.get('leave_type')
        start = data.get('start_date')
        end = data.get('end_date')
        reason = data.get('reason')
        
        LeaveApplication.objects.create(
            teacher=request.user, leave_type=leave_type,
            start_date=start, end_date=end, reason=reason, status='PENDING'
        )
        return JsonResponse({'message': 'Leave application submitted successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
