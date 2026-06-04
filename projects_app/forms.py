from django import forms

from projects_app.constants import ProjectStatus
from projects_app.models import Project

GITHUB_DOMAIN = "github.com"


class ProjectForm(forms.ModelForm):

    status = forms.ChoiceField(
        choices=ProjectStatus.choices,
        widget=forms.Select,
        label="Статус",
    )

    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if url and GITHUB_DOMAIN not in url:
            raise forms.ValidationError(
                "Укажите корректную ссылку на репозиторий GitHub"
            )
        return url