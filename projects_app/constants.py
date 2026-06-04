from django.db import models

MAX_PROJECT_NAME_LENGTH = 200
MAX_SKILL_NAME_LENGTH = 124
PROJECTS_PER_PAGE = 12
SKILLS_AUTOCOMPLETE_LIMIT = 10


class ProjectStatus(models.TextChoices):
    OPEN = "open", "Открыт"
    CLOSED = "closed", "Закрыт"