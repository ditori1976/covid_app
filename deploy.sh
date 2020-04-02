git add .
echo -en "message [ 'update' ] "
read message
if [ -z "$message" ]; then
  message='update'
fi

echo -en "environment [ 'covid-19-dev' ] "
read env
if [ -z "$env" ]; then
  env='covid-19-dev'
fi

git commit -m '$message'
eb deploy $env
