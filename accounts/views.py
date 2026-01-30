from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserLoginForm
from shortener.models import ShortURL
from django.http import HttpResponseRedirect
from django.db import models, IntegrityError
from django.contrib import messages
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

class DashboardView(LoginRequiredMixin, View):
    """
    User dashboard view.

    Lists all short URLs created by the user and allows creating new ones.
    Protected by LoginRequiredMixin.
    """
    template_name = 'dashboard.html'
    
    def get(self, request):
        """
        Display user's short URLs.
        """
        urls = request.user.urls.all()
        return render(request, self.template_name, {'urls': urls})
    
    def post(self, request):
        """
        Create a new short URL.
        """
        original_url = request.POST.get('original_url')
        custom_key = request.POST.get('custom_key')
        
        if original_url:
            try:
                # Convert empty string to None to allow multiple URLs without custom keys
                if not custom_key:
                    custom_key = None
                    
                url = ShortURL.objects.create(original_url=original_url, user=request.user, custom_key=custom_key)
                logger.info(f"URL created by {request.user.email}: {url.short_key or url.custom_key} -> {original_url}")
                messages.success(request, "Short URL created successfully!")
            except IntegrityError:
                logger.warning(f"Duplicate key attempt by {request.user.email}: {custom_key}")
                messages.error(request, f"The alias '{custom_key}' is already taken. Please choose another one.")
        
        return redirect('dashboard')

class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User profile view.
    """
    template_name = 'profile.html'

class RedirectView(View):
    """
    Handles the actual URL redirection.
    
    Looksup the short code (or custom key) and redirects to the original URL.
    Increments the click count on success. Returns 404 if not found or expired.
    """
    def get(self, request, short_code):
        # Handle both short_key and custom_key
        url_obj = ShortURL.objects.filter(models.Q(short_key=short_code) | models.Q(custom_key=short_code)).first()
        if not url_obj or url_obj.is_expired():
            logger.warning(f"404 or Expired access attempt for code: {short_code}")
            return render(request, '404.html', status=404)
        
        url_obj.click_count += 1
        url_obj.save(update_fields=['click_count'])
        logger.info(f"Redirecting {short_code} to {url_obj.original_url}")
        return HttpResponseRedirect(url_obj.original_url)
