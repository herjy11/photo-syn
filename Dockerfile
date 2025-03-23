FROM python:latest
WORKDIR /photo-syn
COPY . /photo-syn
CMD ["python3", "script/deploy_souvenirs.py"]