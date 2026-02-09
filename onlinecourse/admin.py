"""
Admin configuration for the Online Course application.
"""
from django.contrib import admin
# Import any new Models here
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


class ChoiceInline(admin.StackedInline):
    """Inline admin interface for Choice model."""
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    """Inline admin interface for Question model."""
    model = Question
    extra = 2


class LessonInline(admin.StackedInline):
    """Inline admin interface for Lesson model."""
    model = Lesson
    extra = 5


class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model."""
    inlines = [LessonInline, QuestionInline]  # Added QuestionInline here
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    """Admin interface for Lesson model."""
    list_display = ['title']


class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for Question model."""
    inlines = [ChoiceInline]
    list_display = ['content', 'course', 'grade']
    list_filter = ['course']
    search_fields = ['content']


class ChoiceAdmin(admin.ModelAdmin):
    """Admin interface for Choice model."""
    list_display = ['content', 'question', 'is_correct']
    list_filter = ['question', 'is_correct']
    search_fields = ['content']


class SubmissionAdmin(admin.ModelAdmin):
    """Admin interface for Submission model."""
    list_display = ['enrollment', 'get_user', 'get_course']
    list_filter = ['enrollment__course']
    
    def get_user(self, obj):
        """Get the user who made the submission."""
        return obj.enrollment.user.username
    get_user.short_description = 'User'
    
    def get_course(self, obj):
        """Get the course for the submission."""
        return obj.enrollment.course.name
    get_course.short_description = 'Course'


# Register your models here.
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Submission, SubmissionAdmin)
