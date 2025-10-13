from django.apps import AppConfig
import os

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        import tasks.signals

        # --- TEMP: one-time superuser bootstrap via env vars ---
        u = os.getenv("DJANGO_SUPERUSER_USERNAME")
        p = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        e = os.getenv("DJANGO_SUPERUSER_EMAIL", "")

        if u and p:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if not User.objects.filter(username=u).exists():
                    User.objects.create_superuser(u, e, p)
                    print(f"[bootstrap] Superuser '{u}' created.")
            except Exception as ex:
                print(f"[bootstrap] Superuser create skipped/failed: {ex}")