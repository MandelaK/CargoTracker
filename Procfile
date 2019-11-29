release: python carogtracker/manage.py makemigrations authentication branches cargo orders
release: python cargotracker/manage.py migrate

release: python carogtracker/manage.py runscripts create_admin --email="admin@admin.admin"

release: cd carogtracker && ./manage.py run_huey

web: gunicorn cargotracker.wsgi