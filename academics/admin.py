from django.contrib import admin
from .models import Department, ClassSection, Subject , TeachingAssignment


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('department', 'year', 'section')
    list_filter = ('department', 'year')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department')
    list_filter = ('department',)

@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'faculty',
        'subject',
        'class_section',
        'academic_year',
        'semester',
    )

    list_filter = (
        'academic_year',
        'semester',
    )