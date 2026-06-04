import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.utils import paginate_queryset
from projects_app.constants import (PROJECTS_PER_PAGE,
                                    SKILLS_AUTOCOMPLETE_LIMIT, ProjectStatus)
from projects_app.forms import ProjectForm
from projects_app.models import Project, Skill


def project_list(request):
    skill_filter = request.GET.get("skill", "")
    all_skills = Skill.objects.all()

    qs = (
        Project.objects
        .select_related("owner")
        .prefetch_related("skills", "participants")
        .order_by("-created_at")
    )
    if skill_filter:
        qs = qs.filter(skills__name=skill_filter)

    page = paginate_queryset(qs, request, PROJECTS_PER_PAGE)

    return render(request, "projects/project_list.html", {
        "projects": page,
        "page_obj": page,
        "all_skills": all_skills,
        "active_skill": skill_filter,
    })


def project_detail(request, pk):
    qs = Project.objects.select_related("owner").prefetch_related("participants", "skills")
    project = get_object_or_404(qs, pk=pk)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        new_project = form.save(commit=False)
        new_project.owner = request.user
        new_project.save()
        new_project.participants.add(request.user)
        return redirect("projects:detail", pk=new_project.pk)

    return render(request, "projects/create-project.html", {
        "form": form,
        "is_edit": False,
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("projects:detail", pk=project.pk)

    return render(request, "projects/create-project.html", {
        "form": form,
        "is_edit": True,
    })


@login_required
@require_POST
def project_complete(request, pk):
    project = Project.objects.filter(pk=pk, owner=request.user).first()
    if project is None:
        return JsonResponse(
            {"error": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )
    if project.is_open():
        project.status = ProjectStatus.CLOSED
        project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if project is None:
        return JsonResponse(
            {"error": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )
    user = request.user
    already_in = project.participants.filter(pk=user.pk).exists()
    if already_in:
        project.participants.remove(user)
    else:
        project.participants.add(user)
    return JsonResponse({
        "status": "ok",
        "participating": not already_in,
        "participant": not already_in,
    })


def skills_autocomplete(request):
    query = request.GET.get("q", "").strip()
    matched = (
        Skill.objects
        .filter(name__istartswith=query)
        .order_by("name")
        .values("id", "name")[:SKILLS_AUTOCOMPLETE_LIMIT]
    )
    return JsonResponse(list(matched), safe=False)


@login_required
@require_POST
def skill_add(request, pk):
    project = Project.objects.filter(pk=pk, owner=request.user).first()
    if project is None:
        return JsonResponse(
            {"error": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {"error": "Некорректный JSON"},
            status=HTTPStatus.BAD_REQUEST,
        )

    skill_id = body.get("skill_id")
    skill_name = body.get("name", "").strip()

    if skill_id:
        skill = Skill.objects.filter(pk=skill_id).first()
        if skill is None:
            return JsonResponse(
                {"error": "Навык не найден"},
                status=HTTPStatus.NOT_FOUND,
            )
        created = False
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name)
    else:
        return JsonResponse(
            {"error": "Передайте skill_id или name"},
            status=HTTPStatus.BAD_REQUEST,
        )

    already_added = project.skills.filter(pk=skill.pk).exists()
    if not already_added:
        project.skills.add(skill)

    return JsonResponse({
        "skill_id": skill.pk,
        "id": skill.pk,
        "name": skill.name,
        "created": created,
        "added": not already_added,
    })


@login_required
@require_POST
def skill_remove(request, pk, skill_id):
    project = Project.objects.filter(pk=pk, owner=request.user).first()
    if project is None:
        return JsonResponse(
            {"error": "Проект не найден"},
            status=HTTPStatus.NOT_FOUND,
        )

    skill = Skill.objects.filter(pk=skill_id).first()
    if skill is None:
        return JsonResponse(
            {"error": "Навык не найден"},
            status=HTTPStatus.NOT_FOUND,
        )

    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse(
            {"error": "Навык не связан с этим проектом"},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})