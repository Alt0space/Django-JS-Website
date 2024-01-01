from django import forms
from django.forms import ModelForm
from homepage.models import Project
from register.models import Account


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'links', 'creator', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'cols': 44, 'rows': 5}),
            'links': forms.Textarea(attrs={'cols': 44, 'rows': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'type': 'file'})
        }

    def __init__(self, *args, creator=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.creator = creator


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ['username', 'email', 'profile_image', 'hide_email']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError('Email "%s" is already in use.' % account.email)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError('Username "%s" is already in use.' % username)

    def save(self, commit=True):
        account = super(ProfileUpdateForm, self).save(commit=False)
        account.username = self.cleaned_data['username']
        account.email = self.cleaned_data['email'].lower()
        account.profile_image = self.cleaned_data['profile_image']
        account.hide_email = self.cleaned_data['hide_email']
        if commit:
            account.save()
        return account
