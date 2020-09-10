#!/usr/bin/env python3

from aws_cdk import core

from rekognition_processing_app.rekognition_processing_app_stack import RekognitionProcessingAppStack


app = core.App()
RekognitionProcessingAppStack(app, "rekognition-processing-app", env={'region': 'us-west-2'})

app.synth()
