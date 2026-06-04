from django.contrib.auth import (authenticate, get_user_model, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import paginate_queryset
from users_app.constants import USERS_PER_PAGE
from users_app.forms import LoginForm, ProfileEditForm, RegisterForm

User = get_user_model()


def register(request):
    form = RegisterForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:login")

    return render(request, "users/register.html", {"form": form})


def user_login(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        credentials = form.cleaned_data
        user = authenticate(
            request,
            username=credentials["email"],
            password=credentials["password"],
        )
        if user is not None:
            login(request, user)
            return redirect("projects:list")
        form.add_error(None, "Неверный имейл или пароль")

    return render(request, "users/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("projects:list")


def user_list(request):
    all_users = User.objects.filter(is_active=True)
    page_obj = paginate_queryset(all_users, request, USERS_PER_PAGE)
    return render(request, "users/participants.html", {
        "participants": page_obj,
        "page_obj": page_obj,
    })


def user_detail(request, pk):
    profile = get_object_or_404(
        User.objects.prefetch_related("owned_projects"),
        pk=pk,
    )
    return render(request, "users/user-details.html", {"user": profile})


@login_required
def profile_edit(request, pk):
    profile = get_object_or_404(User, pk=pk)
    if request.user.pk != profile.pk:
        return redirect("users:detail", pk=pk)

    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:detail", pk=pk)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def profile_edit_redirect(request):
    return redirect("users:edit", pk=request.user.pk)


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == "POST" and form.is_valid():
        updated_user = form.save()
        update_session_auth_hash(request, updated_user)
        return redirect("users:detail", pk=request.user.pk)

    return render(request, "users/change_password.html", {"form": form})