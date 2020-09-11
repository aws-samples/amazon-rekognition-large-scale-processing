"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json
import boto3
from botocore.exceptions import ClientError
import os
from decimal import Decimal

# Environ Variables
TABLE_NAME = os.environ['TABLE_NAME']
# DynamoDB Resource
dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')


def put_item_dynamodb(item):
    """
    Call DynamoDB API PutItem
    :param item: Dictionary of id, FaceDetails and ResponseMetdata
    :return: DynamoDB PutItem response dict
    """
    dynamodb_table = dynamodb_resource.Table(TABLE_NAME)

    try:
        put_item_response = dynamodb_table.put_item(Item=item)
        return put_item_response

    except ClientError as error:
        return error.response


def parse_message_emotions(message):
    """
    Parse the original SQS message to a DynamoDB compatible dict
    :param message: SQS Message Dict
    :return: Parsed dict to insert into DynamoDB Table
    """
    face_details = message['FaceDetails'][0]
    response_metadata = message['ResponseMetadata']
    # photo_id = str(uuid1()).split('-')[0]
    photo_id = message['s3_object_key']

    item = {'id': photo_id,
            'FaceDetails': face_details,
            'ResponseMetadata': response_metadata}

    # for emotion in face_emotions:
    #    emotion_type = emotion['Type']
    #    emotion_type = emotion_type.lower()
    #    emotion_confidence = emotion['Confidence']
    #    item[emotion_type] = Decimal(str(emotion_confidence))
    #    print(f'{emotion_type} = {emotion_confidence}')

    # Parse the Float values in the message to Decimals
    ddb_item = json.loads(json.dumps(item), parse_float=Decimal)

    return ddb_item


def lambda_handler(event, context):
    """
    This function is call on a SQS Queue event, takes the message of the queue, parses the message and inserts a item
    into dynamoDB
    :param event: SQS Message dict
    :param context: Context dict
    :return: DynamoDB Response PutItem dict
    """
    print(event)
    print(event['Records'][0]['body'][0])
    message_body = json.loads(event['Records'][0]['body'])
    print(message_body)

    item = parse_message_emotions(message_body)
    return put_item_dynamodb(item)
