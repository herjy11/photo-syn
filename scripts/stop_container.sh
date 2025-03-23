name=$1

if [[ -z $name ]];
then
  echo "Please provide a container name"
  exit 1
fi

sudo systemctl stop $name || true
sudo systemctl disable $name || true

sudo docker stop $name || true
sudo docker rm -f $name || true