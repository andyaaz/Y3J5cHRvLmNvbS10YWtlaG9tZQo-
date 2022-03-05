import json
import os
import uuid
import logging

import boto3

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)


def main(event, context):
    LOG.info("EVENT: " + json.dumps(event))

    # query_string_params = event["queryStringParameters"]
    # if query_string_params is not None:
    #     target_url = query_string_params['targetUrl']
    #     if target_url is not None:
    #         return create_short_url(event)
    if event["body"] is not None:
        event["body"] = json.loads(event["body"])

    if event["path"] == '/newurl' and event['httpMethod'] == 'POST':
        if event['body'] is not None and event["body"].get('url') is not None:
            return create_short_url(event)

    path_parameters = event['pathParameters']
    if path_parameters is not None:
        if path_parameters['proxy'] is not None:
            return read_short_url(event)

    return {
        'statusCode': 200,
        'body': 'usage: POST /newurl { "url": "your-url" }'
    }


def create_short_url(event):
    # Pull out the DynamoDB table name from environment
    table_name = os.environ.get('TABLE_NAME')

    # Parse targetUrl
    target_url = event["body"]['url']

    # Create a unique id (take first 8 chars)
    id = str(uuid.uuid4())[0:8]

    # Create item in DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item={'id': id, 'target_url': target_url})

    # Create the redirect URL
    url = "https://" \
        + event["requestContext"]["domainName"] \
        + '/' \
        + event["requestContext"]["stage"] \
        + '/' \
        + id

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            "url": target_url,
            "shortenedUrl": url
        })
    }


def read_short_url(event):
    # Parse redirect ID from path
    id = event['pathParameters']['proxy']

    # Pull out the DynamoDB table name from the environment
    table_name = os.environ.get('TABLE_NAME')

    # Load redirect target from DynamoDB
    ddb = boto3.resource('dynamodb')
    table = ddb.Table(table_name)
    response = table.get_item(Key={'id': id})
    LOG.debug("RESPONSE: " + json.dumps(response))

    item = response.get('Item', None)
    if item is None:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'text/plain'
            },
            'body': 'No redirect found for ' + id
        }

    # Respond with a redirect
    return {'statusCode': 301, 'headers': {'Location': item.get('target_url')}}
