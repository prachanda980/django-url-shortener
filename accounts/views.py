from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView
from .forms import UserRegistrationForm, UserLoginForm
import logging

logger = logging.getLogger('accounts')


class HomeView(TemplateView):
    """
    Renders the public landing page.
    """
    template_name = 'home.html'

class RegisterView(View):
    """
    Handles user registration.

    Displays the registration form and processes new user creation.
    """
    template_name = 'registration/register.html'
    
    def get(self, request):
        return render(request, self.template_name, {'form': UserRegistrationForm()})
    
    def post(self, request):
        """
        Validate form and create a new user.
        """
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            logger.info(f"New user registered and logged in: {user.email}")
            return redirect('dashboard')
        logger.warning("Registration failed: Invalid form data")
        return render(request, self.template_name, {'form': form})

class LoginView(View):
    """
    Handles user login.

    Authenticates existing users via email and password.
    """
    template_name = 'registration/login.html'
    
    def get(self, request):
        return render(request, self.template_name, {'form': UserLoginForm()})
    
    def post(self, request):
        """
        Process login credentials.
        """
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            logger.info(f"User logged in: {user.email}")
            return redirect('dashboard')
        logger.warning(f"Login failed for email: {request.POST.get('email')}")
        return render(request, self.template_name, {'form': form})

class LogoutView(View):
    """
    Logs out the current user.
    """
    def get(self, request):
        if request.user.is_authenticated:
            logger.info(f"User logged out: {request.user.email}")
        logout(request)
        return redirect('login')

class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User profile view.
    """
    template_name = 'profile.html'

