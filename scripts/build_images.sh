set -e

people="people"
souvenirs="souvenirs"
tagp=$people:latest
tags=$souvenirs:latest

echo "Building $people and $souvenirs with tags $tag"

docker build --pull --tag $tagp --target $people .
docker push $tagp
docker build --pull --tag $tags --target $souvenirs .
docker push $tags