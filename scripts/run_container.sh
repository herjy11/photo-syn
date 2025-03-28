set -e

name=$1
echo "Build $name"
run_name=syno.$name

bash /var/services/homes/remy/git_repos/photo-syn/scripts/stop_container.sh $run_name
echo "Start container $run_name"
docker run -d --network=host --name=$run_name -p 127.0.0.1:$3:$3 $name $2 $3

echo "Done"
