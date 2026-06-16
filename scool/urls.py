from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    
    # Authentications
    path('', views.home_redirect, name='home_redirect'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Portal Views
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('teacher-portal/', views.teacher_portal_view, name='teacher_portal'),
    path('student-portal/', views.student_portal_view, name='student_portal'),
    
    # AJAX / API POST Endpoints
    path('api/submit-homework/', views.submit_homework_api, name='submit_homework_api'),
    path('api/mark-attendance/', views.mark_attendance_api, name='mark_attendance_api'),
    path('api/save-marks/', views.save_marks_api, name='save_marks_api'),
    path('api/pay-fee/', views.pay_fee_api, name='pay_fee_api'),
    path('api/send-message/', views.send_message_api, name='send_message_api'),
    path('api/apply-leave/', views.apply_leave_api, name='apply_leave_api'),
]
