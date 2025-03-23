set -e

name=$1

run_name=syno.$name

bash scripts/stop_container.sh $name
echo "Start container $run_name"
docker run -d --name=$run_name $name

echo "Done"
