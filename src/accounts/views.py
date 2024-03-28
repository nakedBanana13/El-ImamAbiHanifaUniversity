from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from .models import CustomUser, Student
from .forms import StudentRegistrationForm
from courses.models import Faculty, StudyYear


class StudentRegistrationView(FormView):
    template_name = 'accounts/register.html'
    form_class = StudentRegistrationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Populate options for faculties and study years
        context['faculties'] = Faculty.objects.all()
        context['study_years'] = StudyYear.objects.all()
        context['qualification'] = Student.QUALIFICATION_CHOICES
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        # Extract user information including the birth_date
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']
        if password != confirm_password:
            form.add_error('confirm_password', "Passwords do not match")
            return self.form_invalid(form)
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        date_of_birth = form.cleaned_data['date_of_birth']
        photo = form.cleaned_data['photo']
        faculty = form.cleaned_data['faculty']
        study_year = form.cleaned_data['study_year']

        # Extract student information
        father_name = form.cleaned_data['father_name']
        country_born = form.cleaned_data['country_born']
        country_of_residence = form.cleaned_data['country_of_residence']
        phone_number = form.cleaned_data['phone_number']
        qualification = form.cleaned_data['qualification']
        language = form.cleaned_data['language']
        certificate_photo = form.cleaned_data['certificate_photo']
        id_photo = form.cleaned_data['id_photo']

        # Save user instance
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=date_of_birth,
            photo=photo
        )

        # Create Student instance and associate it with the user
        Student.objects.create(
            user=user,
            faculty=faculty,
            study_year=study_year,
            father_name=father_name,
            country_born=country_born,
            country_of_residence=country_of_residence,
            phone_number=phone_number,
            qualification=qualification,
            language=language,
            certificate_photo=certificate_photo,
            id_photo=id_photo
        )

        # Save uploaded documents associated with the user
        #documents = form.cleaned_data['documents']
        #if documents:
        #    for doc in documents:
        #        Document.objects.create(user=user, document=doc)

        success_url = reverse('registration_done') + f'?user_id={user.id}'
        return HttpResponseRedirect(success_url)


class RegistrationDoneView(TemplateView):
    template_name = 'accounts/registration_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the user object passed in the URL query parameter
        user_id = self.request.GET.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        context['user'] = user
        return context


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        # Call the parent class's get_success_url method to get the default URL
        redirect_to = self.request.GET.get('next')
        if redirect_to:
            return redirect_to
        success_url = super().get_success_url()


        # Retrieve the authenticated user
        user = self.request.user

        # Determine the user type
        if user.is_authenticated:
            if user.is_student:
                return '/student/dashboard/'  # Redirect to the student dashboard
            return '/course/mine/'  # Redirect to the instructor dashboard
        # If user type is not recognized, redirect to the default success URL
        return success_url


#class ServeDocumentView(View):
#    def get(self, request, username, document_id):
#        document = get_object_or_404(Document, user__username=username, pk=document_id)
#        document_path = document.document.path
#        if os.path.exists(document_path):
#            with open(document_path, 'rb') as f:
#                response = HttpResponse(f.read(), content_type='application/octet-stream')
#                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(document_path)
#                return response
#        else:
#            return HttpResponseNotFound("Document not found")


#class ServePhotoView(View):
#    def get(self, request, username):
#        user = get_object_or_404(CustomUser, username=username)
#        if user.photo:
#            photo_path = user.photo.path
#            if os.path.exists(photo_path):
#                with open(photo_path, 'rb') as f:
#                    response = HttpResponse(f.read(), content_type='image/jpeg')
#                    return response
#        return HttpResponseNotFound("Photo not found")


class UnderReviewView(TemplateView):
    template_name = 'accounts/under_review.html'
