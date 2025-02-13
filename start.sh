# Define the port
# Use 8001 to avoid clashing with atila-django which sometimes runs at same time as atila-django in dev
PORT=8001

source .env
python manage.py runserver $PORT