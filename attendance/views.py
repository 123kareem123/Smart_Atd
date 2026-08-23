from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from academics.models import (
    Department,
    Subject,
    ClassSection,
    TeachingAssignment,
)

from profiles.models import StudentProfile

from .models import AttendanceSession, AttendanceRecord
from .utils import create_attendance_session


from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from academics.models import (
    Department,
    ClassSection,
    Subject,
    TeachingAssignment,
)

from profiles.models import (
    StudentProfile,
    FacultyProfile,
)


# =========================================================
# FACULTY DASHBOARD
# =========================================================

@login_required
def faculty_dashboard(request):

    assignments = TeachingAssignment.objects.filter(
        faculty__user=request.user
    ).select_related(
        'subject',
        'class_section',
        'faculty'
    )

    # Get latest attendance session for every assignment
    for assignment in assignments:

        assignment.latest_session = (
            AttendanceSession.objects
            .filter(
                teaching_assignment=assignment,
                faculty=request.user
            )
            .order_by('-created_at')
            .first()
        )

    return render(
        request,
        'attendance/faculty_dashboard.html',
        {
            'assignments': assignments
        }
    )


# =========================================================
# FACULTY - START ATTENDANCE
# =========================================================

@login_required
def start_attendance(request, assignment_id):

    if request.method != 'POST':

        return JsonResponse(
            {
                'error': 'Only POST requests are allowed.'
            },
            status=405
        )

    # Get assignment belonging to this faculty
    assignment = get_object_or_404(
        TeachingAssignment,
        id=assignment_id,
        faculty__user=request.user
    )

    # Get period
    period = request.POST.get('period')

    if not period:

        return JsonResponse(
            {
                'error': 'Period is required.'
            },
            status=400
        )

    # Convert period to integer
    try:

        period = int(period)

    except ValueError:

        return JsonResponse(
            {
                'error': 'Invalid period.'
            },
            status=400
        )

    # =====================================================
    # CLOSE OLD ACTIVE SESSION FOR SAME CLASS/PERIOD
    # =====================================================

    AttendanceSession.objects.filter(
        teaching_assignment=assignment,
        faculty=request.user,
        period=period,
        is_active=True
    ).update(
        is_active=False
    )

    # =====================================================
    # CREATE NEW SESSION
    # =====================================================

    session = create_attendance_session(
        teaching_assignment=assignment,
        faculty=request.user,
        period=period
    )

    return JsonResponse(
        {
            'message':
                'Attendance started successfully.',

            'session_id':
                session.id,

            'otp':
                session.otp,

            'expires_at':
                session.otp_expires_at.isoformat(),
        }
    )


# =========================================================
# FACULTY - VIEW ATTENDANCE
# =========================================================

@login_required
def faculty_attendance_records(request, session_id):

    # Make sure session belongs to logged-in faculty
    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        faculty=request.user
    )

    # Get all students in this class
    students = StudentProfile.objects.filter(
        class_section=
            session.teaching_assignment.class_section
    ).select_related(
        'user'
    ).order_by(
        'student_id'
    )

    # Get attendance records
    records = AttendanceRecord.objects.filter(
        session=session
    ).select_related(
        'student',
        'student__user'
    )

    # Create dictionary for quick lookup
    record_map = {
        record.student_id: record
        for record in records
    }

    attendance_data = []

    # =====================================================
    # BUILD ATTENDANCE DATA
    # =====================================================

    for student in students:

        record = record_map.get(
            student.id
        )

        if record:

            status = record.status
            marked_at = record.marked_at

        else:

            # If session has not ended yet,
            # show as ABSENT temporarily.
            status = 'ABSENT'
            marked_at = None

        attendance_data.append(
            {
                'student': student,
                'status': status,
                'marked_at': marked_at
            }
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    total_students = len(
        attendance_data
    )

    present_count = sum(
        1
        for item in attendance_data
        if item['status'] == 'PRESENT'
    )

    absent_count = (
        total_students -
        present_count
    )

    if total_students > 0:

        percentage = round(
            (
                present_count /
                total_students
            ) * 100,
            2
        )

    else:

        percentage = 0

    return render(
        request,
        'attendance/faculty_view_attendance.html',
        {
            'session':
                session,

            'attendance_data':
                attendance_data,

            'total_students':
                total_students,

            'present_count':
                present_count,

            'absent_count':
                absent_count,

            'percentage':
                percentage,
        }
    )


# =========================================================
# FACULTY - END ATTENDANCE
# =========================================================

@login_required
def end_attendance(request, session_id):

    # Only POST allowed
    if request.method != 'POST':

        return JsonResponse(
            {
                'error':
                    'Only POST requests are allowed.'
            },
            status=405
        )

    # Get session
    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        faculty=request.user
    )

    # =====================================================
    # CHECK IF ALREADY ENDED
    # =====================================================

    if not session.is_active:

        return JsonResponse(
            {
                'error':
                    'Attendance session is already ended.'
            },
            status=400
        )

    # =====================================================
    # GET ALL STUDENTS IN CLASS
    # =====================================================

    students = StudentProfile.objects.filter(
        class_section=
            session.teaching_assignment.class_section
    )

    # =====================================================
    # FIND STUDENTS WHO ALREADY MARKED PRESENT
    # =====================================================

    present_student_ids = set(
        AttendanceRecord.objects.filter(
            session=session
        ).values_list(
            'student_id',
            flat=True
        )
    )

    # =====================================================
    # MARK EVERY OTHER STUDENT ABSENT
    # =====================================================

    absent_records = []

    for student in students:

        if student.id not in present_student_ids:

            absent_records.append(
                AttendanceRecord(
                    session=session,
                    student=student,
                    status='ABSENT'
                )
            )

    # Create absent records
    if absent_records:

        AttendanceRecord.objects.bulk_create(
            absent_records,
            ignore_conflicts=True
        )

    # =====================================================
    # CLOSE SESSION
    # =====================================================

    session.is_active = False

    session.save(
        update_fields=[
            'is_active'
        ]
    )

    return JsonResponse(
        {
            'message':
                'Attendance session ended successfully.',

            'absent_count':
                len(absent_records)
        }
    )


# =========================================================
# FACULTY - ATTENDANCE HISTORY
# =========================================================

@login_required
def faculty_attendance_history(request):

    sessions = AttendanceSession.objects.filter(
        faculty=request.user
    ).select_related(
        'teaching_assignment__subject',
        'teaching_assignment__class_section'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'attendance/attendance_history.html',
        {
            'sessions':
                sessions
        }
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@login_required
def student_dashboard(request):

    student = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    # Active attendance sessions
    active_sessions = AttendanceSession.objects.filter(
        teaching_assignment__class_section=student.class_section,
        is_active=True,
        otp_expires_at__gt=timezone.now()
    ).select_related(
        'teaching_assignment__subject',
        'teaching_assignment__class_section',
        'faculty'
    ).order_by(
        '-created_at'
    )

    # All attendance records of this student
    attendance_records = AttendanceRecord.objects.filter(
        student=student
    )

    # Statistics
    total_classes = attendance_records.count()

    present_count = attendance_records.filter(
        status='PRESENT'
    ).count()

    absent_count = attendance_records.filter(
        status='ABSENT'
    ).count()

    if total_classes > 0:

        attendance_percentage = round(
            (present_count / total_classes) * 100,
            2
        )

    else:

        attendance_percentage = 0

    return render(
        request,
        'attendance/student_dashboard.html',
        {
            'student': student,
            'active_sessions': active_sessions,

            'total_classes': total_classes,
            'present_count': present_count,
            'absent_count': absent_count,
            'attendance_percentage':
                attendance_percentage,
        }
    )


# =========================================================
# STUDENT - MARK ATTENDANCE
# =========================================================

@login_required
def mark_attendance(request):

    # Only POST allowed
    if request.method != 'POST':

        return JsonResponse(
            {
                'error':
                    'Only POST requests are allowed.'
            },
            status=405
        )

    # Get student
    student = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    # Get submitted values
    session_id = request.POST.get(
        'session_id'
    )

    otp = request.POST.get(
        'otp'
    )

    # =====================================================
    # CHECK INPUT
    # =====================================================

    if not session_id or not otp:

        return JsonResponse(
            {
                'error':
                    'Session ID and OTP are required.'
            },
            status=400
        )

    # =====================================================
    # GET SESSION
    # =====================================================

    session = get_object_or_404(
        AttendanceSession,
        id=session_id
    )

    # =====================================================
    # CHECK SESSION ACTIVE
    # =====================================================

    if not session.is_active:

        return JsonResponse(
            {
                'error':
                    'This attendance session is no longer active.'
            },
            status=400
        )

    # =====================================================
    # CHECK OTP EXPIRY
    # =====================================================

    if timezone.now() > session.otp_expires_at:

        return JsonResponse(
            {
                'error':
                    'OTP has expired.'
            },
            status=400
        )

    # =====================================================
    # CHECK OTP
    # =====================================================

    if str(otp).strip() != str(
        session.otp
    ).strip():

        return JsonResponse(
            {
                'error':
                    'Invalid OTP.'
            },
            status=400
        )

    # =====================================================
    # CHECK STUDENT CLASS
    # =====================================================

    if (
        session.teaching_assignment.class_section
        != student.class_section
    ):

        return JsonResponse(
            {
                'error':
                    'This attendance session is not for your class.'
            },
            status=403
        )

    # =====================================================
    # CHECK DUPLICATE ATTENDANCE
    # =====================================================

    already_marked = (
        AttendanceRecord.objects.filter(
            session=session,
            student=student
        ).exists()
    )

    if already_marked:

        return JsonResponse(
            {
                'message':
                    'Attendance already marked.',

                'status':
                    'PRESENT'
            },
            status=200
        )

    # =====================================================
    # CREATE PRESENT RECORD
    # =====================================================

    AttendanceRecord.objects.create(
        session=session,
        student=student,
        status='PRESENT'
    )

    return JsonResponse(
        {
            'message':
                'Attendance marked successfully.',

            'status':
                'PRESENT'
        }
    )


# =========================================================
# STUDENT - ATTENDANCE HISTORY
# =========================================================
@login_required
def student_attendance_history(request):

    student = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    # All attendance records of this student
    records = AttendanceRecord.objects.filter(
        student=student
    ).select_related(
        'session',
        'session__teaching_assignment',
        'session__teaching_assignment__subject',
        'session__teaching_assignment__class_section',
        'session__faculty'
    ).order_by(
        '-session__date',
        '-session__period'
    )

    # =====================================================
    # OVERALL STATISTICS
    # =====================================================

    total_classes = records.count()

    present_count = records.filter(
        status='PRESENT'
    ).count()

    absent_count = records.filter(
        status='ABSENT'
    ).count()

    if total_classes > 0:

        percentage = round(
            (present_count / total_classes) * 100,
            2
        )

    else:

        percentage = 0


    # =====================================================
    # SUBJECT-WISE ATTENDANCE
    # =====================================================

    subject_data = {}

    for record in records:

        subject = (
            record.session
            .teaching_assignment
            .subject
        )

        subject_id = subject.id

        if subject_id not in subject_data:

            subject_data[subject_id] = {
                'subject_name':
                    subject.name,

                'subject_code':
                    subject.code,

                'total':
                    0,

                'present':
                    0,

                'absent':
                    0,

                'percentage':
                    0,
            }

        subject_data[subject_id]['total'] += 1

        if record.status == 'PRESENT':

            subject_data[
                subject_id
            ]['present'] += 1

        else:

            subject_data[
                subject_id
            ]['absent'] += 1


    # Calculate percentage
    for subject in subject_data.values():

        if subject['total'] > 0:

            subject['percentage'] = round(
                (
                    subject['present']
                    /
                    subject['total']
                ) * 100,
                2
            )


    return render(
        request,
        'attendance/student_attendance_history.html',
        {
            'student':
                student,

            'records':
                records,

            'total_classes':
                total_classes,

            'present_count':
                present_count,

            'absent_count':
                absent_count,

            'percentage':
                percentage,

            'subject_data':
                subject_data.values(),
        }
    )
    
@login_required
def select_class(request):

    departments = Department.objects.all().order_by("name")

    selected_year = request.GET.get("year")
    selected_department = request.GET.get("department")
    selected_section = request.GET.get("section")
    selected_semester = request.GET.get("semester")

    sections = ClassSection.objects.none()

    # =========================================================
    # GET SECTIONS
    # =========================================================

    if selected_year and selected_department:

        try:

            year = int(selected_year)

            sections = ClassSection.objects.filter(
                department_id=selected_department,
                year=year
            ).order_by("section")

        except (ValueError, TypeError):

            sections = ClassSection.objects.none()

    # =========================================================
    # SAVE CLASS SECTION
    # =========================================================

    if selected_section:

        try:

            class_section = get_object_or_404(
                ClassSection,
                id=selected_section
            )

            request.session["class_section_id"] = (
                class_section.id
            )

        except (ValueError, TypeError):

            return redirect("select_class")

    # =========================================================
    # SAVE SEMESTER
    # =========================================================

    if selected_semester:

        try:

            semester = int(selected_semester)

            if semester < 1:

                return redirect("select_class")

            request.session["semester"] = semester

        except (ValueError, TypeError):

            request.session.pop(
                "semester",
                None
            )

            return redirect("select_class")

    # =========================================================
    # GO TO SUBJECT PAGE
    # =========================================================

    if selected_section and selected_semester:

        return redirect("select_subject")

    # =========================================================
    # RENDER CLASS PAGE
    # =========================================================

    return render(
        request,
        "attendance/select_class.html",
        {
            "departments": departments,

            "sections": sections,

            "selected_year":
                selected_year,

            "selected_department":
                selected_department,

            "selected_section":
                selected_section,

            "selected_semester":
                selected_semester,
        }
    )

@login_required
def select_subject(request):

    # =========================================================
    # GET CLASS SECTION FROM SESSION
    # =========================================================

    class_section_id = request.session.get(
        "class_section_id"
    )

    semester = request.session.get(
        "semester"
    )

    if not class_section_id or not semester:

        return redirect("select_class")


    # =========================================================
    # GET CLASS SECTION
    # =========================================================

    class_section = get_object_or_404(
        ClassSection,
        id=class_section_id
    )


    # =========================================================
    # GET FACULTY PROFILE
    # =========================================================

    try:

        faculty = request.user.faculty_profile

    except FacultyProfile.DoesNotExist:

        return render(
            request,
            "attendance/select_subject.html",
            {
                "assignments": [],
                "class_section": class_section,
                "error": "Faculty profile not found."
            }
        )


    # =========================================================
    # GET SUBJECTS FROM CSV DATABASE
    # =========================================================

    subjects = Subject.objects.filter(
        department=class_section.department,
        year=class_section.year,
        semester=semester
    ).order_by("code")


    # =========================================================
    # CREATE TEACHING ASSIGNMENTS AUTOMATICALLY
    # =========================================================

    assignments = []

    academic_year = request.session.get(
        "academic_year",
        "2026-27"
    )


    for subject in subjects:

        assignment, created = (
            TeachingAssignment.objects.get_or_create(

                faculty=faculty,

                subject=subject,

                class_section=class_section,

                semester=semester,

                defaults={
                    "academic_year": academic_year
                }
            )
        )

        assignments.append(assignment)


    # =========================================================
    # HANDLE SUBJECT SELECTION
    # =========================================================

    if request.method == "POST":

        assignment_id = request.POST.get(
            "assignment_id"
        )

        period = request.POST.get(
            "period"
        )

        if not assignment_id:

            return render(
                request,
                "attendance/select_subject.html",
                {
                    "assignments": assignments,
                    "class_section": class_section,
                    "error": "Please select a subject."
                }
            )


        if not period:

            return render(
                request,
                "attendance/select_subject.html",
                {
                    "assignments": assignments,
                    "class_section": class_section,
                    "error": "Please select a period."
                }
            )


        assignment = get_object_or_404(
            TeachingAssignment,
            id=assignment_id,
            faculty=faculty,
            class_section=class_section
        )


        # =====================================================
        # STORE ASSIGNMENT + PERIOD
        # =====================================================

        request.session[
            "teaching_assignment_id"
        ] = assignment.id

        request.session[
            "period"
        ] = int(period)


        # =====================================================
        # START ATTENDANCE
        # =====================================================

        return redirect(
            "start_attendance"
        )


    # =========================================================
    # DISPLAY SUBJECTS
    # =========================================================

    return render(
        request,
        "attendance/select_subject.html",
        {
            "assignments": assignments,

            "class_section": class_section,

            "semester": semester,
        }
    )