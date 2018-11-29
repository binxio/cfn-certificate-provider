# Custom::Certificate
The `Custom::Certificate` creates a ACM Certificate.

It is identical to [AWS::CertificateManager::Certificate](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html), except for the fact that it will return immediately after creating the certificate request.


## Syntax
To declare this entity in your AWS CloudFormation template, use the same syntax as [AWS::CertificateManager::Certificate](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html):

```yaml
  Certificate:
    Type: Custom::Certificate
    Properties:
      DomainName: !Ref DomainName
      ValidationMethod: DNS
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-certificate-provider'
```

## Properties
You can specify the following properties:

    "DomainName" - to create a certificate for (required).
    "ValidationMethod" - to validate the certificate with (required to be DNS).
    "ServiceToken" - pointing to the function implementing this resource (required).
    "Region" - region name where the certificate should be created, e.g. "us-east-1" (optional).

For all other properties, check out [AWS::CertificateManager::Certificate](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html).
 
## Return values
The resource returns the ARN of the Certificate.
