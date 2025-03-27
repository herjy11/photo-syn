name=$1

if [[ -z $name ]];
then
  echo "Please provide a container name"
  exit 1
fi

sudo -S systemctl stop $name || true
sudo -S systemctl disable $name || true

sudo -S docker stop $name || true
sudo -S docker rm -f $name || true