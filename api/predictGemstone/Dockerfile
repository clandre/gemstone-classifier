# syntax=docker/dockerfile:1

FROM public.ecr.aws/lambda/python:3.7

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

#RUN pip3 install https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow_cpu-2.6.0-cp37-cp37m-manylinux2010_x86_64.whl

COPY app.py ./

CMD [ "app.handler" ]