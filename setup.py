import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="rekognition_processing_app",
    version="0.0.1",

    description="A sample CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "rekognition_processing_app"},
    packages=setuptools.find_packages(where="rekognition_processing_app"),

    install_requires=[
        "aws-cdk.aws-s3",
        "aws-cdk.aws-s3-notifications",
        "aws-cdk.aws-lambda",
        "aws-cdk.aws-lambda-event-sources",
        "aws-cdk.aws-sqs",
        "aws-cdk.aws-dynamodb",
        "aws-cdk.aws-iam"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
