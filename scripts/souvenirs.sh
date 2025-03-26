set -e

name=$1

run_name=syno.$name

bash scripts/stop_container.sh $run_name
echo "Start container $run_name"
sudo docker run -d --network=host --name=$run_name $name

echo "Done"
