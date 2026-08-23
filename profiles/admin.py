from django.contrib import admin

from .models import StudentProfile, FacultyProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'user',
        'department',
        'class_section',
        'year',
    )

    list_filter = (
        'department',
        'year',
    )

    search_fields = (
        'student_id',
        'user__username',
        'user__first_name',
        'user__last_name',
    )


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = (
        'faculty_id',
        'user',
        'department',
    )

    list_filter = (
        'department',
    )

    search_fields = (
        'faculty_id',
        'user__username',
        'user__first_name',
        'user__last_name',
    )