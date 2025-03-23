name=$1

if [[ -z $name ]];
then
  echo "Please provide a container name"
  exit 1
fi

systemctl stop $name || true
systemctl disable $name || true

docker stop $name || true
docker rm -f $name || true