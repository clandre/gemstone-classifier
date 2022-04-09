# syntax=docker/dockerfile:1

FROM public.ecr.aws/lambda/python:3.7

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY app.py ./

COPY model.h5 ./

COPY gemstone_enc.json ./

CMD [ "app.handler" ]