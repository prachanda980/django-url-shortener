from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseRedirect
from django.db import models, IntegrityError
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import ShortURL
import logging

logger = logging.getLogger('shortener')

class DashboardView(LoginRequiredMixin, View):
    """
    User dashboard view.
    Lists all short URLs created by the user and allows creating new ones.
    """
    template_name = 'dashboard.html'
    
    def get(self, request):
        urls = request.user.urls.all()
        return render(request, self.template_name, {'urls': urls})
    
    def post(self, request):
        original_url = request.POST.get('original_url')
        custom_key = request.POST.get('custom_key')
        
        if original_url:
            try:
                if not custom_key:
                    custom_key = None
                    
                url = ShortURL.objects.create(original_url=original_url, user=request.user, custom_key=custom_key)
                logger.info(f"URL created by {request.user.email}: {url.short_key or url.custom_key} -> {original_url}")
                messages.success(request, "Short URL created successfully!")
            except IntegrityError:
                logger.warning(f"Duplicate key attempt by {request.user.email}: {custom_key}")
                messages.error(request, f"The alias '{custom_key}' is already taken. Please choose another one.")
        
        return redirect('dashboard')

class RedirectView(View):
    """
    Handles the actual URL redirection.
    """
    def get(self, request, short_code):
        url_obj = ShortURL.objects.filter(models.Q(short_key=short_code) | models.Q(custom_key=short_code)).first()
        if not url_obj or url_obj.is_expired():
            logger.warning(f"404 or Expired access attempt for code: {short_code}")
            return render(request, '404.html', status=404)
        
        url_obj.click_count += 1
        url_obj.save(update_fields=['click_count'])
        
        logger.info(f"Redirecting {short_code} to {url_obj.original_url}")

        return HttpResponseRedirect(url_obj.original_url)

