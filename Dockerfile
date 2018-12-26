FROM python:3
ADD kostal-piko-dataexport.py /
ADD requirements.txt /
RUN pip install -r requirements.txt
CMD [ "python", "./kostal-piko-dataexport.py" ]
