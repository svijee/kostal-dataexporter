FROM python:3.12.3-slim-bookworm

COPY requirements.txt kostal-piko-dataexport.py /

RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "./kostal-piko-dataexport.py" ]
