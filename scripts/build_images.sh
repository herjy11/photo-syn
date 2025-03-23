set -e

target=$1
tag=$target:latest

echo "Building $target with tags $tag"

docker build --pull --tag $tag --target $target .
docker push $tag