# Atila Core Service

## Quickstart

`pip install -r requirements.txt`
`python manage.py runserver 8001`

## Setup your Database

Follow [this tutorial](https://tutorial-extensions.djangogirls.org/en/optional_postgresql_installation/) 
([tutorial on Github](https://github.com/DjangoGirls/tutorial-extensions/tree/master/en/optional_postgresql_installation))
to install Postgres and add 
to a Django project.

See [this tutorial](https://blog.nextideatech.com/how-to-create-a-django-app-and-connect-it-to-a-database/) to add some pieces missing in the previously mentioned tutorial such as:
`GRANT ALL PRIVILEGES ON DATABASE atila TO name;`

1. Mac: Install [Postgres.app](https://postgresapp.com/downloads.html). 

1. `psql`

Run the following commands inside the sql terminal

1. `CREATE USER name WITH PASSWORD 'passwprd';`

2. `CREATE DATABASE atila OWNER name;`
3. `GRANT ALL PRIVILEGES ON DATABASE atila TO name;`
4. Update `settigs.py` (this should already be done but including for completeness)

Confirm the commands work by seeing the first word in the command in your response.

```python
import os
POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'atila',
        'USER': POSTGRES_USERNAME,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
    }
}
```
4. `pip install psycopg2`. Verify it works with: `python -c "import psycopg2"`
5. `python manage.py migrate`
6. `python manage.py createsuperuser --username name`
## Deploying to Heroku

`git push heroku master`

Push from a non-master branch: `git push heroku <branch_name>:master`

Worth noting also, when you're ready to go back to master you need to do: `git push -f heroku master:master`

See [Stack Overflow answer for more context](https://stackoverflow.com/a/14593582/5405197)

## Deploying Postgres to Heroku
1. Check that a database doesn't already exist with `heroku addons`
2. `heroku addons:create heroku-postgresql:mini`
3. Add to `Procfile`:`release: python manage.py migrate`