"""
Models for the Online Course application.
"""
import sys
from django.utils.timezone import now
from django.conf import settings
import uuid

try:
    from django.db import models
except Exception as err:
    print(f"There was an error loading django modules. Do you have django installed? Error: {err}")
    sys.exit()


# Instructor model
class Instructor(models.Model):
    """Model representing an instructor."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    """Model representing a learner/student."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.user.username},{self.occupation}"


# Course model
class Course(models.Model):
    """Model representing a course."""
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return f"Name: {self.name}, Description: {self.description}"


# Lesson model
class Lesson(models.Model):
    """Model representing a lesson within a course."""
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"{self.title} (Course: {self.course.name})"


# Question model
class Question(models.Model):
    """Model representing a question in an exam."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    grade = models.IntegerField(default=50)

    def __str__(self):
        return f"Question: {self.content}"

    def is_get_score(self, selected_ids):
        """
        Calculate if the learner gets the score for this question.
        
        Args:
            selected_ids: List of selected choice IDs
            
        Returns:
            bool: True if all correct choices are selected and no incorrect ones
        """
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(
            is_correct=True, 
            id__in=selected_ids
        ).count()
        return all_answers == selected_correct


# Choice model
class Choice(models.Model):
    """Model representing a choice for a question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.content} (Question: {self.question.content})"


# Enrollment model
class Enrollment(models.Model):
    """Model representing a user's enrollment in a course."""
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.name} on {self.date_enrolled}"


# Submission model
class Submission(models.Model):
    """Model representing an exam submission."""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return f"Submission by {self.enrollment.user.username} for {self.enrollment.course.name}"
    