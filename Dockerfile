FROM python:3.12.2-slim-bookworm

COPY requirements.txt /
COPY kostal-piko-dataexport.py /

RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "./kostal-piko-dataexport.py" ]
