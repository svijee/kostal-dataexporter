FROM python:3.8-slim-buster

ADD requirements.txt /
ADD kostal-piko-dataexport.py /

RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "./kostal-piko-dataexport.py" ]
