FROM python:3.7-slim-buster
ADD kostal-piko-dataexport.py /
ADD requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "./kostal-piko-dataexport.py" ]
