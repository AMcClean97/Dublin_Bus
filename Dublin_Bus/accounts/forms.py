from django import forms
from django.contrib.auth import get_user_model

# check for unique name and username

User = get_user_model()


class RegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "user-password"
            }
        )
    )

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "user-confirm-password"
            }
        )
    )


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "id": "user-password"
            }
        )
    )

    # check username is correct
    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username_iexact=username)
        if not qs.exists():
            raise forms.ValidationError("This is not a valid username,"
                                        "please choose another.")
        return username

    # ensure username and password are correct
    # def clean(self):
    # username = self.cleaned_data.get("username")
    #     password = self.cleaned_data.get("password")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(username_iexact=email)
        if not qs.exists():
            raise forms.ValidationError("This is not a valid email,"
                                        "please choose another.")
        return email
