# Atila Core Service

## Quickstart

`pip install -r requirements.txt`
`python manage.py runserver 8001`

## Deploying to Heroku

Push from a non-master branch: `git push heroku <branch_name>:master`

Worth noting also, when you're ready to go back to master you need to do: `git push -f heroku master:master`

See [Stack Overflow anser for more context](https://stackoverflow.com/a/14593582/5405197)