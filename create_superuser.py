import os
import django

if not os.getenv("DJANGO_SUPERUSER_USERNAME") or not os.getenv("DJANGO_SUPERUSER_PASSWORD"):
    print("Superuser env vars not set. Skipping.")
    exit(0)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "readersstation.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv("DJANGO_SUPERUSER_USERNAME")
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if User.objects.filter(username=username).exists():
    print("Superuser already exists. Skipping.")
else:
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created.")
