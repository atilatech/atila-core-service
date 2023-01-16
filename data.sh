load_remote_data(){
 # example: load_remote_data atlas.document
 # example: load_remote_data atlas.document
 if [ -z "$2" ]
   then
     heroku run python manage.py dumpdata $1 --indent 4 --natural-primary --natural-foreign\
      --app atila-core-service > dumpdata.json ;
 else
     heroku run python manage.py dumpdata $1 --pks $2 --indent 4 --natural-primary --natural-foreign\
      --app atila-core-service > dumpdata.json;
 fi
}

load_local_data(){
 # example: load_local_data atlas.document
 if [ -z "$2" ]
   then
     python manage.py dumpdata $1 --indent 4 --natural-primary --natural-foreign > dumpdata.json ;
 else
     python manage.py dumpdata $1 --pks $2 --indent 4 --natural-primary --natural-foreign > dumpdata.json;
 fi
}