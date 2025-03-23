set -e

people="people"
souvenirs="souvenirs"
tagp=$people:latest
tags=$souvenirs:latest

echo "Building $people and $souvenirs with tags $tag"

docker build --pull -t $tagp --target -f $people .
docker push $tagp
docker build --pull -t $tags --target -f $souvenirs .
docker push $tags