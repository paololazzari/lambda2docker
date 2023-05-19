FROM python:3.11-alpine

ADD setup.py .
ADD src src

RUN pip install -e . 

ENTRYPOINT ["lambda2docker"]
CMD ["--help"]