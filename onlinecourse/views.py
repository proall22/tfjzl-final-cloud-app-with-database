from django.shortcuts import render
from django.http import HttpResponseRedirect
# Import any new Models here
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except User.DoesNotExist:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(
                username=username, 
                first_name=first_name, 
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(
        reverse(viewname='onlinecourse:course_details', args=(course.id,))
    )


def submit(request, course_id):
    """
    Create an exam submission record for a course enrollment.
    """
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    # Get the enrollment object
    enrollment = Enrollment.objects.get(user=user, course=course)
    
    # Create a new submission object
    submission = Submission.objects.create(enrollment=enrollment)
    
    # Collect the selected choices from the exam form
    selected_choice_ids = extract_answers(request)
    
    # Add each selected choice object to the submission object
    selected_choices = Choice.objects.filter(id__in=selected_choice_ids)
    submission.choices.set(selected_choices)
    
    # Save the submission
    submission.save()
    
    # Redirect to show_exam_result view with the submission id
    return HttpResponseRedirect(
        reverse(
            viewname='onlinecourse:exam_result', 
            args=(course_id, submission.id,)
        )
    )


def show_exam_result(request, course_id, submission_id):
    """
    Display exam results and calculate the score.
    """
    context = {}
    
    # Get course and submission objects
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Get selected choices from the submission
    selected_choices = submission.choices.all()
    
    # Calculate total score
    total_score = 0
    all_questions = course.question_set.all()
    
    for question in all_questions:
        # Check if the learner gets the score for this question
        selected_ids = selected_choices.filter(question=question).values_list('id', flat=True)
        if question.is_get_score(list(selected_ids)):
            total_score += question.grade
    
    # Add data to context
    context['course'] = course
    context['selected_ids'] = [choice.id for choice in selected_choices]
    context['grade'] = total_score
    
    # Prepare question results for template
    question_results = []
    for question in all_questions:
        # Get correct choices for this question
        correct_choices = question.choice_set.filter(is_correct=True)
        # Get selected choices for this question
        selected_for_question = selected_choices.filter(question=question)
        # Check if question is answered correctly
        selected_ids = selected_for_question.values_list('id', flat=True)
        is_correct = question.is_get_score(list(selected_ids))
        
        question_results.append({
            'question': question,
            'correct_choices': correct_choices,
            'selected_choices': selected_for_question,
            'is_correct': is_correct,
            'grade': question.grade if is_correct else 0
        })
    
    context['question_results'] = question_results
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)


def extract_answers(request):
    """
    Extract selected choice IDs from the request object.
    """
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice_'):
            value = request.POST[key]
            choice_id = int(value)
            submitted_answers.append(choice_id)
    return submitted_answers
    