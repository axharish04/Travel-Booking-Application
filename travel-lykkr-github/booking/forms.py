from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Booking, TravelOption
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from crispy_forms.bootstrap import FormActions


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'username',
            'email',
            'password1',
            'password2',
            FormActions(
                Submit('submit', 'Register', css_class='btn btn-primary')
            )
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'phone',
            'address',
            'date_of_birth',
            FormActions(
                Submit('submit', 'Update Profile', css_class='btn btn-primary')
            )
        )


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'email',
            FormActions(
                Submit('submit', 'Update Information', css_class='btn btn-primary')
            )
        )


class TravelSearchForm(forms.Form):
    TYPE_CHOICES = [('', 'All Types')] + TravelOption.TRAVEL_TYPES
    
    source = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'From'}))
    destination = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'To'}))
    travel_type = forms.ChoiceField(choices=TYPE_CHOICES, required=False)
    departure_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('source', css_class='form-group col-md-3 mb-0'),
                Column('destination', css_class='form-group col-md-3 mb-0'),
                Column('travel_type', css_class='form-group col-md-3 mb-0'),
                Column('departure_date', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Search', css_class='btn btn-primary')
            )
        )


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['number_of_seats', 'passenger_names', 'contact_email', 'contact_phone']
        widgets = {
            'passenger_names': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter passenger names separated by commas'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.travel_option = kwargs.pop('travel_option', None)
        super().__init__(*args, **kwargs)
        
        if self.travel_option:
            self.fields['number_of_seats'].widget.attrs['max'] = min(10, self.travel_option.available_seats)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'number_of_seats',
            'passenger_names',
            Row(
                Column('contact_email', css_class='form-group col-md-6 mb-0'),
                Column('contact_phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Confirm Booking', css_class='btn btn-success')
            )
        )
    
    def clean_number_of_seats(self):
        seats = self.cleaned_data['number_of_seats']
        if self.travel_option and seats > self.travel_option.available_seats:
            raise forms.ValidationError(f'Only {self.travel_option.available_seats} seats available.')
        return seats
    
    def clean_passenger_names(self):
        names = self.cleaned_data['passenger_names']
        number_of_seats = self.cleaned_data.get('number_of_seats', 0)
        
        if names:
            name_list = [name.strip() for name in names.split(',') if name.strip()]
            if len(name_list) != number_of_seats:
                raise forms.ValidationError(f'Please provide exactly {number_of_seats} passenger names.')
        
        return names
