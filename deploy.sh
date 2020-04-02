git add .
echo -en "message [ 'update' ] "
read message
if [ -z "$message" ]; then
  message='update'
fi

git commit -m $message
eb deploy $0
