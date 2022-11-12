from django.shortcuts import render, redirect
from .models import Profile
from .forms import MeetForm, CustomUserCreationForm
from .models import Meet
from django.contrib.auth import logout, authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .token import account_activation_token
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.contrib.auth import get_user_model


def logout_view(request):
    logout(request)
    return redirect("meetter:login")


def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
    else:
        return redirect('meetter:login')


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("form is valid finaly")
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link for your account was sent to your mail'
            message = render_to_string('registration/acc_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get("email")
            EmailMessage(mail_subject, message, to=[to_email]).send()
            return HttpResponse("Activation link was sent to your email")
        else:
            print(form.errors)
            return render(
                request, "registration/register.html",
                {"form": CustomUserCreationForm()}
            )
    else:
        return render(
            request, "registration/register.html",
            {"form": CustomUserCreationForm()}
        )


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')




def dashboard(request):
    return render(request, 'base.html')


def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    return render(request, 'meetter/profile_list.html', {'profiles': profiles})


def main(request):
    if request.user.is_anonymous:
        return redirect('meetter:login')
    if request.method == "POST":
        form = MeetForm(request.POST)
        print(request.POST)
        print(request.user.id)
        if form.is_valid():
            meet = form.save(commit=False)
            meet.creator_user = request.user
            meet.save()
            return redirect('meetter:main')

    new_meet_form = MeetForm()
    current_user = request.user
    meets_querry_sets = [profile.user.meets.all() for profile in current_user.profile.follows.all()]
    meets = Meet.objects.filter(
        creator_user__profile__in=request.user.profile.follows.all()
    ).order_by("-pub_date")
    return render(request, 'meetter/main.html', {"meets": meets, "MeetForm": new_meet_form})


def profile_detail(request, pk):

    print("Page is loaded")

    if not hasattr(request.user, 'profile'):
        missing_profile = Profile(user=request.user)
        missing_profile.save()

    profile = Profile.objects.get(pk=pk)
    if request.method == "POST":
        current_user_profile = request.user.profile
        data = request.POST
        action = data.get("follow")
        if action == "follow":
            current_user_profile.follows.add(profile)
        elif action == "unfollow":
            current_user_profile.follows.remove(profile)
        current_user_profile.save()
    else:
        print("didn't get through Post")
    return render(request, 'meetter/profile_detail.html', {'profile': profile})
