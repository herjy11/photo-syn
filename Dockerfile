FROM python:latest AS base

WORKDIR /photo-syn

COPY . /photo-syn

RUN pip install /photo-syn

FROM base AS souvenirs
ENTRYPOINT ["python3", "/photo-syn/scripts/deploy_souvenirs.py"]

FROM base AS people
ENTRYPOINT ["python3", "/photo-syn/scripts/deploy_people_albums.py"]