import json
import pytest

from aws_cdk import core
from rekognition-processing-app.rekognition_processing_app_stack import RekognitionProcessingAppStack


def get_template():
    app = core.App()
    RekognitionProcessingAppStack(app, "rekognition-processing-app")
    return json.dumps(app.synth().get_stack("rekognition-processing-app").template)


def test_sqs_queue_created():
    assert("AWS::SQS::Queue" in get_template())


def test_sns_topic_created():
    assert("AWS::SNS::Topic" in get_template())
