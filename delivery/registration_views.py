from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import DeliveryPartnerRegistrationForm, DeliveryPartnerProfileUpdateForm
from .models import DeliveryPartner

class DeliveryPartnerRegistrationView(CreateView):
    """Registration view for delivery partners"""
    form_class = DeliveryPartnerRegistrationForm
    template_name = 'delivery/register.html'
    success_url = reverse_lazy('delivery:registration_success')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request, 
            'Registration successful! Your account is pending verification. '
            'You will be notified once approved.'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register as Delivery Partner'
        return context

@csrf_protect
def delivery_partner_registration_success(request):
    """Success page after delivery partner registration"""
    return render(request, 'delivery/registration_success.html')

@login_required
def delivery_partner_profile(request):
    """Delivery partner profile view"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        messages.error(request, 'Delivery partner profile not found')
        return redirect('delivery:register')
    
    if request.method == 'POST':
        form = DeliveryPartnerProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=partner
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('delivery:profile')
    else:
        form = DeliveryPartnerProfileUpdateForm(instance=partner)
    
    context = {
        'partner': partner,
        'form': form,
        'title': 'My Profile'
    }
    
    return render(request, 'delivery/profile.html', context)

@login_required
def delivery_partner_verification_status(request):
    """Check verification status"""
    try:
        partner = request.user.delivery_partner
    except DeliveryPartner.DoesNotExist:
        return render(request, 'delivery/verification_required.html')
    
    context = {
        'partner': partner,
        'title': 'Verification Status'
    }
    
    return render(request, 'delivery/verification_status.html', context)
