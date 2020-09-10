
# Welcome to your CDK Python project!

This is a blank project for Python development with CDK.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

### Architecture

![Architecture Diagram](docs/diagram_arch.png)

### Usage

#### Prerequisites

- A AWS Account 
- AWS CDK for Python
- Python 3.6 or latter
- IAM Privileges to deploy the components of the architecture

#### Deployment
```
$ npm install -g aws-cdk
$ cd <Mod>
$ pip install -r requirements.txt    # Best to do this in a virtualenv
$ cdk deploy                         # Deploys the CloudFormation template
```

#### Cleanup
```
cd <Mod>
$ cdk destroy                        # This comand will delete all the deployed resources
```

### Making changes to the code and customization

The [contributing guidelines](CONTRIBUTING.md) contains some instructions about how to run the front-end locally and make changes to the back-end stack.

## Contributing

Contributions are more than welcome. Please read the [code of conduct](CODE_OF_CONDUCT.md) and the [contributing guidelines](CONTRIBUTING.md).


## License Summary

This library is licensed under the MIT-0 License. See the LICENSE file.