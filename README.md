# Atila Core Service
The primary backend service for Atila apps.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/atilatech/atila-core-service)

## Atlas

To see how [Atlas](https://atlas.atila.ca/) works, see: [Atlas: Find Anything on Youtube](https://atila.ca/blog/tomiwa/atlas), [atlas app inside this repo](https://github.com/atilatech/atila-core-service/tree/master/atlas), [Atlas Notebooks](https://github.com/atilatech/atila-core-service/tree/master/atlas/notebooks) and [atlas-ui](https://github.com/atilatech/atlas-ui).

## Quickstart

`source install.sh ; source start.sh`

or:
`pip install -r requirements.txt`
`python manage.py runserver`

Verify it works by navigating to http://127.0.0.1:8000/api/atila/users/
or running the following command:

```shell
curl -H 'Accept: application/json; indent=4' -u username:password http://127.0.0.1:8000/api/atila/users/
```

## Services

Atila Core Service contains the following services:

1. [Atlas: Find Anything on Youtube](https://github.com/atilatech/atila-core-service/tree/master/atlas)

## Authentication
Verify that token authentication works. By pasting the following command and `copy-pasting` access into jwt.io.
Don't do this for production JWT tokens.

```shell
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}' \
  http://127.0.0.1:8000/api/token/

# ...
{
  "refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3NDE3NTUzMCwiaWF0IjoxNjc0MDg5MTMwLCJqdGkiOiJkOWEyYmU1M2IyNzU0Mzc3OGI5NDc1MWQ4ZWI1N2MwOSIsInVzZXJfaWQiOjF9.ILWp0YkhXCmLmFWf3o1IOdIM5UDN4EDpnxJiuXXRvfo",
  "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc0MDg5NDMwLCJpYXQiOjE2NzQwODkxMzAsImp0aSI6ImZlOTM3MDJkZWI4MzRjZTM5ODVmOTRjZjJhMGM4OTk5IiwidXNlcl9pZCI6MX0.5ytin4jxFv-h_iu3dWTfcvZnMo0-YwedK6GSKcyTUYk"
}
```

Try it on a protected view
```shell
curl \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc0MTMzNjk1LCJpYXQiOjE2NzQxMzMzOTUsImp0aSI6ImVhNjlmZDU0Y2JmZTRiZTk5M2JlZWZjZjk3ZGIyMzFiIiwidXNlcl9pZCI6MSwidXNlcnByb2ZpbGVfaWQiOiJkaXpnbGxkb2c2c211ZnFtIn0.Vf36M0KinwrWzRFcNe9oFZ-p8a0zpcfNWzpqtpihiJk" \
  http://127.0.0.1:8000/api/atila/users/1/
# ...
{"id":1,"username":"admin","email":"info@atila.ca"}
```

## Setup your Database

Follow [this tutorial](https://tutorial-extensions.djangogirls.org/en/optional_postgresql_installation/) 
([tutorial on Github](https://github.com/DjangoGirls/tutorial-extensions/tree/master/en/optional_postgresql_installation))
to install Postgres and add 
to a Django project.

See [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-20-04) 
to add some pieces missing in the previously mentioned tutorial such as: `GRANT ALL PRIVILEGES`

1. Mac: Install [Postgres.app](https://postgresapp.com/downloads.html). 

1. `psql`

Run the following commands inside the sql terminal

1. `CREATE USER admin WITH PASSWORD 'admin';`

2. `CREATE DATABASE atila OWNER admin;`
3. `GRANT ALL PRIVILEGES ON DATABASE atila TO admin;`
```bash
ALTER ROLE admin SET client_encoding TO 'utf8';
ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE admin SET timezone TO 'UTC';
```
4. Create a `DJANGO_SECRET_KEY`: `python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
4. Update `settings.py` (this should already be done but including for completeness)

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
6. `python manage.py createsuperuser --username admin`

### Permission denied for table django

```bash
psql atila -c "GRANT ALL ON ALL TABLES IN SCHEMA public to admin";
psql atila -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to admin";
psql atila -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to admin";
```

## Troubleshooting


### django.db.utils.OperationalError: could not connect to server: Connection refused
If you get the following error make sure your Postgres server is running:
```text
django.db.utils.OperationalError: could not connect to server: Connection refused
        Is the server running on host "localhost" (::1) and accepting
        TCP/IP connections on port 5432?
```

source: https://stackoverflow.com/a/39070745/5405197
## Deploying to Heroku

`git push heroku master`

Push from a non-master branch: `git push heroku <branch_name>:master`

Worth noting also, when you're ready to go back to master you need to do: `git push -f heroku master:master`

See [Stack Overflow answer for more context](https://stackoverflow.com/a/14593582/5405197)

## Deploying Postgres to Heroku
1. Check that a database doesn't already exist with `heroku addons`
2. `heroku addons:create heroku-postgresql:mini`
3. Add to `Procfile`:`release: python manage.py migrate`

## Loading Data

### Seed Database with Pre-Transcribed Videos

`python manage.py loaddata atlas/data/transcribed_videos.json`

To run any of the following commands, you must first run `source data.sh`.

### Download Data from Prod

`load_remote_data atlas.document ; python manage.py loaddata dumpdata.json`

## Export Local Data to Local File
`dump_local_data atlas.document`

### Upload Local Data to Prod
`upload_local_data_to_prod <filename>`
`<filename>` is optional. If none is provided, it defaults to `dumpdata.json`.

see: https://stackoverflow.com/a/49152992/5405197

## Running Standalone scripts
Sometimes you just want to quickly run a function without running the entire Django server or submitting a request.

You can run this in the `quick_scripts.py` file using `python quick_scripts.py`

`python scripts_send_email.py`

You can also make your own file and put the following at the top of the file, making sure to
put any Django-specific imports after you call `django.setup()`

```python
import django
import os
import sys


sys.path.append("atila")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atila.settings")
django.setup()
```

## Troubleshooting

### Permission denied for table django
```bash
psql atila
ALTER TABLE public.atlas_document OWNER TO admin;
# or to change multiple owners in a schema
ALTER SCHEMA public OWNER TO admin;
# verify it works
select * from pg_tables;
```

One Liner:
```bash
for tbl in `psql -qAt -c "select tablename from pg_tables where schemaname = 'public';" atila` ; do  psql -c "alter table \"$tbl\" owner to admin" atila ; done
# verify it works
psql atila
select * from pg_tables;
```
see: [PostgreSQL: Modify OWNER on all tables simultaneously in PostgreSQL](https://stackoverflow.com/a/2686185/5405197)

The following may not work, leaving for the sake of completeness:
```bash
psql atila -c "GRANT ALL ON ALL TABLES IN SCHEMA public to admin";
psql atila -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to admin";
psql atila -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to admin";
```
