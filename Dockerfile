FROM python:latest AS base

WORKDIR /photo-syn

COPY . /photo-syn

RUN pip install /photo-syn

FROM base AS souvenirs
CMD python3 /photo-syn/scripts/deploy_souvenirs.py

FROM base AS people
CMD python3 /photo-syn/scripts/deploy_people_albums.py