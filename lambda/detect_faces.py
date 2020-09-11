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
import logging
import boto3
from botocore.exceptions import ClientError
import os
from time import sleep
from random import randint

# Environ Variables
SQS_RESPONSE_QUEUE = os.environ['SQS_RESPONSE_QUEUE']
MAX_RETRIES = 3

# Boto 3 Resources / Clients
rekognition_client = boto3.client('rekognition', region_name='us-east-1')
sqs_resource = boto3.resource('sqs')


def detect_faces_rekognition(s3_bucket_name, s3_object_key, attributes='ALL'):
    """
    Detect Rekognition faces with Exponential backoff + jitter and max retries
    :param s3_bucket_name: str that contains the bucket name
    :param s3_object_key: str that contains the object key name
    :param attributes: str used to retrieve all Amazon Rekognition labels on DetectFaces API
    :return: Image Response dict / Error dict
    """

    retry_rekgonition = True
    num_retries = 0

    while retry_rekgonition and num_retries <= MAX_RETRIES:

        try:

            print(f'Detecting {s3_bucket_name}/{s3_object_key}')

            image_response = rekognition_client.detect_faces(Image={
                'S3Object': {
                    'Bucket': s3_bucket_name,
                    'Name': s3_object_key
                }
            },
                Attributes=[attributes]
            )

            print(image_response)

            # Check if the call to Rekognition returned any value
            if image_response:
                # Add the object key in the message to send to Write Queue
                image_response['s3_object_key'] = s3_object_key

                # Send Mesage to SQS Queue
                send_response_sqs(image_response)
                retry_rekgonition = False

            return image_response

        except ClientError as error:

            if num_retries == MAX_RETRIES:
                raise error

            if error.__class__.__name__ == 'ThrottlingException' or\
                    error.__class__.__name__ == 'ProvisionedThroughputExceededException':

                num_retries += 1
                wait_time = 0.10 * (2 ** num_retries)
                rand_jitter = randint(200, 1000) / 1000
                sleep(wait_time + rand_jitter)

            elif error.__class__.__name__ == 'LimitExceededException':
                print(error.__class__.__name__)
                print(error.response)
                retry_rekgonition = False
                return error.response

            else:
                print(error.response)
                retry_rekgonition = False
                return error.response


def send_response_sqs(message_body):
    """
    Sends the response from Amazon Rekognition DetectFaces to a SQS queue
    :param message_body: Message to send to SQS queue dict
    :return:
    """
    # Get the queue
    queue = sqs_resource.get_queue_by_name(QueueName=SQS_RESPONSE_QUEUE)

    # Send a new message
    try:
        response = queue.send_message(MessageBody=json.dumps(message_body))
        message_id = response.get('MessageId')

        print(f'Sent Message {message_id}')

    except ClientError as error:
        print(error.response)
        return error.response


def lambda_handler(event, context):
    """
    This function is call on a SQS Queue event, takes the message of the queue, parses the Amazon S3 PutObject event
    message, then calls Amazon Rekognition DetectFaces API, finally sends a message to the Write Results SQS Queue
    :param event: S3 PutObject Event dict
    :param context: Context dict
    :return: Amazon Rekognition DetectFaces Response Dict
    """

    print(event)
    print(event['Records'][0]['body'][0])
    message_body = json.loads(event['Records'][0]['body'])
    print(message_body)

    s3_bucket_name = message_body['Records'][0]['s3']['bucket']['name']
    s3_object_key = message_body['Records'][0]['s3']['object']['key']

    print(f'Bucket = {s3_bucket_name}')
    print(f'Object Key = {s3_object_key}')

    return detect_faces_rekognition(s3_bucket_name, s3_object_key)
