from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from datetime import datetime
from dateutil.relativedelta import relativedelta


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(UserCreationForm, self).clean()
        birthday = cleaned_data.get('date_of_birth')
        if birthday > (datetime.now().date + relativedelta(years=18)):
            self.add_error('date_of_birth', 'you must be atleast 18 years old')

        phone_number = cleaned_data.get('phone_number', None)
        if phone_number:
            if 10 > len(str(phone_number)) < 9:
                self.add_error('phone_number', 'phone number must be 9 digits')

    class Meta:
        model = User
        fields = ('email', 'first_name', 'middle_name', 'last_name',
                  'date_of_birth', 'phone_number', 'is_landlord')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(UserChangeForm, self).clean()
        birthday = cleaned_data.get('date_of_birth')
        if birthday > (datetime.now().date + relativedelta(years=18)):
            self.add_error('date_of_birth', 'you must be atleast 18 years old')

        phone_number = cleaned_data.get('phone_number', None)
        if phone_number:
            if not len(str(phone_number)) == 9:
                self.add_error('phone_number', 'phone number must be 9 digits')

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'middle_name',
            'last_name',
            'date_of_birth',
            'phone_number',
        )

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', )
    list_filter = ()
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': ()
        }),
        ('Permissions', {
            'fields': ('is_admin', )
        }),
    )
    search_fields = ('email', )
    ordering = ('email', )
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
