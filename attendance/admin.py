from django.contrib import admin

from .models import AttendanceSession , AttendanceRecord

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = (
        'teaching_assignment',
        'faculty',
        'date',
        'period',
        'otp',
        'otp_expires_at',
        'is_active',
    )

    list_filter = (
        'date',
        'period',
        'is_active',
    )

    search_fields = (
        'otp',
        'faculty__username',
    )

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'session',
        'status',
        'marked_at',
    )

    list_filter = (
        'status',
        'session__date',
    )

    search_fields = (
        'student__student_id',
    )