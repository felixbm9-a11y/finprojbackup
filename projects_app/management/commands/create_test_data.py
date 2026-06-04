from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects_app.models import Project, Skill

User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей и проекты"

    def handle(self, *args, **kwargs):
        # Навыки
        skill_list = ["Python", "Django", "JavaScript", "Vue.js", "PostgreSQL", "Docker", "FastAPI", "Redis"]
        skills = {name: Skill.objects.get_or_create(name=name)[0] for name in skill_list}

        # Тестовые пользователи
        users_data = [
            {
                "email": "ivan@teamfinder.ru",
                "name": "Иван",
                "surname": "Петров",
                "password": "finder2024",
            },
            {
                "email": "maria@teamfinder.ru",
                "name": "Мария",
                "surname": "Соколова",
                "password": "finder2024",
            },
            {
                "email": "dmitry@teamfinder.ru",
                "name": "Дмитрий",
                "surname": "Волков",
                "password": "finder2024",
            },
        ]

        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "name": data["name"],
                    "surname": data["surname"],
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(f"  Создан пользователь: {user.email}")
            users.append(user)

        # Проекты
        projects_data = [
            {
                "name": "MeetUp Planner",
                "description": "Сервис для организации встреч внутри команды разработчиков.",
                "owner": users[0],
                "skills": ["Python", "Django", "PostgreSQL"],
            },
            {
                "name": "Code Review Bot",
                "description": "Телеграм-бот, который автоматически проверяет pull request'ы.",
                "owner": users[0],
                "skills": ["Python", "FastAPI", "Docker"],
            },
            {
                "name": "Habit Tracker",
                "description": "Приложение для отслеживания полезных привычек с напоминаниями.",
                "owner": users[1],
                "skills": ["Python", "Django", "Vue.js"],
            },
            {
                "name": "Link Vault",
                "description": "Сервис для хранения и каталогизации полезных ссылок.",
                "owner": users[1],
                "skills": ["JavaScript", "Vue.js", "Redis"],
            },
            {
                "name": "Deploy Dashboard",
                "description": "Дашборд для мониторинга состояния сервисов в реальном времени.",
                "owner": users[2],
                "skills": ["Python", "FastAPI", "Docker"],
            },
            {
                "name": "Open Dictionary",
                "description": "Открытый словарь терминов для начинающих разработчиков.",
                "owner": users[2],
                "skills": ["Python", "Django", "JavaScript"],
            },
        ]

        for data in projects_data:
            project, created = Project.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "owner": data["owner"],
                    "status": "open",
                },
            )
            if created:
                project.participants.add(data["owner"])
                for skill_name in data["skills"]:
                    project.skills.add(skills[skill_name])
                self.stdout.write(f"  Создан проект: {project.name}")

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно созданы!"))
        self.stdout.write("Логины: ivan@teamfinder.ru / maria@teamfinder.ru / dmitry@teamfinder.ru")
        self.stdout.write("Пароль для всех: finder2024")