set -e

name=$1
echo "Build $name"
run_name=syno.$name

bash scripts/stop_container.sh $run_name
echo "Start container $run_name"
sudo docker run -d --name=$run_name -p $2:$3:$3 $name $2 $3

echo "Done"
