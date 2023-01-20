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

dump_local_data(){
 # example: dump_local_data atlas.document
 if [ -z "$2" ]
   then
     python manage.py dumpdata $1 --indent 4 --natural-primary --natural-foreign > dumpdata.json ;
 else
     python manage.py dumpdata $1 --pks $2 --indent 4 --natural-primary --natural-foreign > dumpdata.json;
 fi
}

upload_local_data_to_prod(){
  # see: https://stackoverflow.com/a/49152992/5405197
  # example upload_local_data_to_prod
  # example upload_local_data_to_prod dumpdata_2.json
  cat ${1:=dumpdata.json} | heroku run --no-tty -a ${1:=atila-core-service} -- python manage.py loaddata --format=json -
}