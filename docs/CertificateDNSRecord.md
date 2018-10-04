# Custom::CertificateDNSRecord
The `Custom::CertificateDNSRecord` returns the DNS record for a domain name on a certificate.

## Syntax
To declare this entity in your AWS CloudFormation template, use the following syntax:

```yaml
  DomainDNSRecord:
    Type: Custom::CertificateDNSRecord
    Properties:
      CertificateArn: !Ref Certificate
      DomainName: !Ref DomainName
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-certificate-provider'
```

## Properties
You can specify the following properties:

    "CertificateArn" - of the certificate to get the DNS record for (required).
    "DomainName" - on the certificate to get the DNS record for (required).
    "ServiceToken" - pointing to the function implementing this resource (required).
 
## Return value
The resource returns the Name of the DNS record.  

## Attributes
With 'Fn::GetAtt' the following values are available:

- `Name` - of the DNS recordD for the DomainName on the certificate.
- `Type` - of the DNS record for DomainName on the certificate.
- `Value` - of the DNS record for DomainName on the certificate.

For more information about using Fn::GetAtt, see [Fn::GetAtt](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).
