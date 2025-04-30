from django import forms
from .models import TaskerProfile,CustomerProfile


class ProfileForm(forms.ModelForm):
	class Meta:
		model=TaskerProfile
		fields= ['phone_number', 'address', 'bio', 'profile_image', 'availability_start', 'availability_end', 'city','services']
		widgets= {

            'services': forms.SelectMultiple(attrs={ 'class': 'form-control dropdown', 
                'placeholder': 'Select services...',
                'multiple': True }), # To allow multiple selection}), 
        }


class CustProfileForm(forms.ModelForm):
	class Meta:
		model=CustomerProfile
		fields=['phone_number', 'address','city']