from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse

from courses.models import Category, Course, Lesson, Tag,Comment,Like
from django.utils.html import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path


class LessonForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Lesson
        fields = '__all__'


# Register your models here.
class MyCourse(admin.ModelAdmin):
    list_display = ['id', 'subject', 'description', 'image', 'category', 'created_date']
    search_fields = ['subject']
    list_filter = ['id', 'created_date']
    list_editable = ['subject']
    readonly_fields = ['image_view']

    def image_view(self, course):
        return mark_safe(f"<img src = '/static/{course.image.name}' width = '200'/>")


class MyLessonAdmin(admin.ModelAdmin):
    form = LessonForm


class CourseAppAdminSite(admin.AdminSite):
    site_header = 'Hệ thống khoá học trực tuyến'

    def get_urls(self):
        return [
            path('course-stats/', self.stats_view)
        ] + super().get_urls()

    def stats_view(self, request):
        count = Course.objects.filter(active=True).count()

        stats = Course.objects.annotate(lesson_count=Count('my_lesson')).values('id', 'subject', 'lesson_count')
        return TemplateResponse(
                     request, 'admin/course-stats.html',
            {'course_count': count, 'course_stats': stats})


admin_site = CourseAppAdminSite(name='myadmin')
admin_site.register(Category)
admin_site.register(Tag)
admin_site.register(Comment)
admin_site.register(Like)
admin_site.register(Course, MyCourse)
admin_site.register(Lesson, MyLessonAdmin)
# admin.site.register(Category)
# admin.site.register(Course, MyCourse)
# admin.site.register(Lesson, MyLessonAdmin)
