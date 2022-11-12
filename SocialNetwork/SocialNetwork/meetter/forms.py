from django import forms
from .models import Meet
from django.contrib.auth.models import User
from django.contrib.auth.forms import  UserCreationForm


class MeetForm(forms.ModelForm):
    body = forms.CharField(required=True,
                           widget=forms.widgets.Textarea(
                               attrs={"placeholder": "Type something...",
                                      "class": "textarea is-success is-medium"}),
                           label="")

    class Meta:
        model = Meet
        exclude = ('creator_user',)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
