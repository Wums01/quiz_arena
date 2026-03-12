#!/usr/bin/env bash
set -e

echo "=== INSTALLING REQUIREMENTS ==="
pip install -r requirements.txt

echo "=== RUNNING MIGRATIONS ==="
python manage.py migrate

echo "=== LOADING QUESTIONS FIXTURE ==="
python manage.py loaddata questions.json --verbosity 2 || true

echo "=== CREATING SUPERUSER IF NEEDED ==="
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); username='wums'; email='obebe.elizabeth@gmail.com'; password='WumsAdmin123!'; User.objects.filter(username=username).exists() or User.objects.create_superuser(username, email, password)"

echo "=== COLLECTING STATIC FILES ==="
python manage.py collectstatic --noinput