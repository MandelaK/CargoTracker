release: python carogtracker/manage.py makemigrations authentication branches cargo orders
release: python cargotracker/manage.py migrate

release: python cargotracker/manage.py runscripts create_admin --email="admin@admin.admin"

worker: python cargotracker/manage.py run_huey

web: gunicorn cargotracker.wsgi