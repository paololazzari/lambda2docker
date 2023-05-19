# lambda2docker

Generate a Dockerfile from an AWS lambda function

## Install

```bash
pip install lambda2docker
```

## Usage

```bash
$ lambda2docker --lambda-name my-lambda-function --region us-east-1 --flavor alpine
Dockerfile generated in output directory /tmp/tmpnl30z9us
```

or using docker:

```bash
$ docker run --rm -it -v "/root/.aws:/root/.aws:ro" -v "/tmp":/tmp plazzari/lambda2docker --lambda-name my-lambda-function --region us-east-1 --flavor alpine
Dockerfile generated in output directory /tmp/tmpnl30z9us
```

## Example

Let's say we have deployed this Python function:

```python
# lambda_function.py
import requests
def lambda_handler(event, context):
    print("Hello from lambda")
```

alongside a layer which contains `requests`.

To generate a Dockerfile:

```bash
$ lambda2docker --lambda-name my-lambda-function --region us-east-1 --flavor alpine
Dockerfile generated in output directory /tmp/tmpnl30z9us
```

Let's inspect what was generated:

```bash
$ tree /tmp/tmpnl30z9us
/tmp/tmpnl30z9us
├── Dockerfile
├── src
│   ├── lambda_function.py
│   └── requirements.txt
└── wrapper_entrypoint.py

1 directory, 4 files

$ cat /tmp/tmpnl30z9us/Dockerfile
FROM python:3.8-alpine
WORKDIR /data
ADD src src
ADD wrapper_entrypoint.py wrapper_entrypoint.py
RUN pip install -r src/requirements.txt
ENTRYPOINT ["python3"]

$ cat /tmp/tmpnl30z9us/src/requirements.txt
requests==2.30.0
```

This Dockerfile is buildable:

```bash
$ pushd /tmp/tmpnl30z9us
$ docker build -t my-lambda-container .
$ popd
```

## Supported runtimes

[x] python3.7, python3.8, python3.9, python3.10<br>
[] TODO: nodejs12.x, nodejs14.x, nodejs16.x, nodejs18.x<br>
[] TODO: java8, java8.al2, java11, java17<br>
[] TODO: dotnet5.0, dotnet6, dotnet7, dotnetcore3.1<br>
[] TODO: go1.x<br>
[] TODO: ruby2.7<br>
