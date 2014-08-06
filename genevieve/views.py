from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView

def home(request):
     return render_to_response(
         'home.html'
         )

def auto_login(request):
     if request.user.is_authenticated():
          return HttpResponseRedirect('/file_process')

class UserCreateView(CreateView):
    """
    A view that creates a new user, logs them in, and redirects them to the
    root URL.
    """
    model = User
    form_class = UserCreationForm
    template_name = 'signup.html'

    def form_valid(self, form):
        form.save()

        user = authenticate(username=form.cleaned_data.get('username'),
                            password=form.cleaned_data.get('password1'))

        if user is not None:
            login(self.request, user)

        return HttpResponseRedirect('/file_process')
