




from django.urls import path
from . import views


urlpatterns = [
    path(
    'faculty/select-subject/',
    views.select_subject,
    name='select_subject'
),

    path(
        'faculty/select-class/',
        views.select_class,
        name='select_class'
    ),
   

    # Faculty
    path(
        'start/<int:assignment_id>/',
        views.start_attendance,
        name='start_attendance'
    ),

    path(
        'faculty/dashboard/',
        views.faculty_dashboard,
        name='faculty_dashboard'
    ),

    path(
        'faculty/attendance/<int:session_id>/',
        views.faculty_attendance_records,
        name='faculty_attendance_records'
    ),

    path(
        'faculty/attendance/<int:session_id>/end/',
        views.end_attendance,
        name='end_attendance'
    ),

    path(
        'faculty/history/',
        views.faculty_attendance_history,
        name='faculty_attendance_history'
    ),

    # Student
    path(
        'student/dashboard/',
        views.student_dashboard,
        name='student_dashboard'
    ),

    path(
        'student/attendance/',
        views.mark_attendance,
        name='mark_attendance'
    ),

    path(
        'student/history/',
        views.student_attendance_history,
        name='student_attendance_history'
    ),

    path(
    'faculty/attendance/<int:session_id>/end/',
    views.end_attendance,
    name='end_attendance'
),

]