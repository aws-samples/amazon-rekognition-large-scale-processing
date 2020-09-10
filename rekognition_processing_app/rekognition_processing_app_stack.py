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

from aws_cdk import (
    aws_sqs as sqs,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_lambda_event_sources as _lambda_events,
    aws_s3_notifications as s3n,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    core
)


class RekognitionProcessingAppStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create image bucket
        image_bucket = s3.Bucket(self, 'inbound_image_s3_bucket')

        # Create the image processing queue
        image_process_queue = sqs.Queue(
            self, "image_process_queue",
            visibility_timeout=core.Duration.seconds(300),
            retention_period=core.Duration.days(1)
        )

        # Create the image response queue
        response_queue = sqs.Queue(
            self, "results_queue",
            visibility_timeout=core.Duration.seconds(300),
            retention_period=core.Duration.days(1)
        )

        # Set the put object notification to the SQS Queue
        image_bucket.add_event_notification(event=s3.EventType.OBJECT_CREATED_PUT,
                                            dest=s3n.SqsDestination(image_process_queue))

        # Define the AWS Lambda to call Amazon Rekognition DetectFaces
        detect_faces_lambda = _lambda.Function(self, 'detect_faces',
                                               runtime=_lambda.Runtime.PYTHON_3_7,
                                               handler='detect_faces.lambda_handler',
                                               code=_lambda.Code.asset('./lambda'),
                                               timeout=core.Duration.seconds(30),
                                               environment={'SQS_RESPONSE_QUEUE': response_queue.queue_name},
                                               reserved_concurrent_executions=50
                                               )

        # Set SQS image_process_queue Queue as event source for detect_faces_lambda
        detect_faces_lambda.add_event_source(_lambda_events.SqsEventSource(image_process_queue,
                                                                           batch_size=1))

        # Allow response queue messages from lambda
        response_queue.grant_send_messages(detect_faces_lambda)

        # Allow lambda to call Rekognition by adding a IAM Policy Statement
        detect_faces_lambda.add_to_role_policy(iam.PolicyStatement(actions=['rekognition:*'],
                                                                   resources=['*']))
        # Allow lambda to read from S3
        image_bucket.grant_read(detect_faces_lambda)

        # Define the DynamoDB Table
        results_table = dynamodb.Table(self, 'detect_faces_results',
                                       table_name='detect_faces_results',
                                       partition_key=dynamodb.Attribute(name='id', type=dynamodb.AttributeType.STRING),
                                       read_capacity=200,
                                       write_capacity=200
                                       )

        # Define the AWS Lambda to write results into DyanamoDB results_table
        write_results_lambda = _lambda.Function(self, 'write_results',
                                               runtime=_lambda.Runtime.PYTHON_3_7,
                                               handler='write_results.lambda_handler',
                                               code=_lambda.Code.asset('./lambda'),
                                               timeout=core.Duration.seconds(30),
                                               environment={'TABLE_NAME': results_table.table_name}
                                               )

        # Set SQS response_queue Queue as event source for write_results_lambda results_table
        write_results_lambda.add_event_source(_lambda_events.SqsEventSource(response_queue,
                                                                            batch_size=1))

        # Allow AWS Lambda write_results_lambda to Write to Dynamodb
        results_table.grant_write_data(write_results_lambda)

        # Allow AWS Lambda write_results_lambda to read messages from the SQS response_queue Queue
        response_queue.grant_consume_messages(write_results_lambda)

        # Output to Amazon S3 Image Bucket
        core.CfnOutput(self, 'cdk_output',
                       value=image_bucket.bucket_name,
                       description='Input Amazon S3 Image Bucket')