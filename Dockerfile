FROM python:3.7-slim-buster

ADD requirements.txt /
ADD kostal-piko-dataexport.py /

RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "./kostal-piko-dataexport.py" ]
