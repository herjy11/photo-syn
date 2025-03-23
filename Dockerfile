FROM python:latest AS base

WORKDIR /photo-syn

COPY . /photo-syn

FROM base AS souvenirs
CMD python3 script/deploy_souvenirs.py

FROM base AS photos
CMD /scripts/deploy_people_albums.py