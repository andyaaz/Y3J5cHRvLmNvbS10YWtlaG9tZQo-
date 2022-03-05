# URL Shortener

this implementation is based on an [aws cdk example](https://github.com/aws-samples/aws-cdk-examples) with no VPC and Route53 setup and some changes to lambda function

- [app.py](./app.py) defines the URL shortener service using AWS Constructs for Lambda, API Gateway and DynamoDB.

## Setup

Create and source a Python virtualenv on MacOS and Linux, and install python dependencies:

```
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Install the latest version of the AWS CDK CLI:

```shell
$ npm i -g aws-cdk
```

## Deployment

At this point, you should be able to deploy all the stacks in this app using:

```shell
$ TABLE_NAME=urls cdk deploy '*'
```
