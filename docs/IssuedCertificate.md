# Custom::IssuedCertificate
The `Custom::IssuedCertificate` waits until a certificate reaches the state 'ISSUED'.

No actually resource is created. If you need to use the issued certificate, please let your ELB or CloudFront Distribution depend on this resource. It will return the ARN of the Certificate.

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
  IssuedCertificate:
    Type: Custom::IssuedCertificate
    Properties:
      CertificateArn: !Ref Certificate
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-certificate-provider'
```

## Properties
You can specify the following properties:

    "CertificateArn" - of the certificate to wait for (required).
    "ServiceToken" - pointing to the function implementing this resource (required).
 
No other properties are required.

## Return Value
The resource returns the ARN of the Certificate.

