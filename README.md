# Custom Certificate Provider with DNS validation support
AWS Certificate Manager is a great service that allows the creation and renewal of certificates
to be automated. It provides two ways of validating a certificate request: through email and through DNS.

When you are creating immutable infrastructure, the email validation method is a no-go as it requires
human intervention. The DNS validation is of course the way to go! With 'Route53' we have full
control over the DNS domain and can create the required records.

Although the CloudFormation [AWS::CertificateManager::Certificate](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-certificatemanager-certificate.html) resource allow you to specify that you want DNS validation, it does not 
reveal the DNS records that you need to create. It writes them in the CloudFormation log
file so that another human has to collect them and manually update the DNS record.

With this custom provider you can fully automated the creation of certificates with CloudFormation!


## How do I request certificates fully automatically?

As a prerequisite, you need to have the hosted zones for the domain names on your certificate in Route53. If you have that,
you can fully automate the provisioning of certificates, with the following resources:

1. [Custom::Certificate](docs/Certificate.md) to request a certificate without waiting for it to be issued
3. [Custom::CertificateDNSRecord](docs/CertificateDNSRecord.md) which will obtain the DNS record for a domain name on the certificate.
3. [Custom::IssuedCertificate](docs/IssuedCertificate.md) which will activately wait until the certificate is issued.
4. [AWS::Route53::ResourceRecordSet](https://docs.aws.amazon.com/Route53/latest/APIReference/API_ResourceRecordSet.html) to create the validation DNS record.

Checkout the sample in [cloudformation/demo-stack.yaml](cloudformation/demo-stack.yaml).

## Installation
To install this custom resource, type:

```sh
aws cloudformation create-stack \
	--capabilities CAPABILITY_IAM \
	--stack-name cfn-certificate-provider \
	--template-body file://cloudformation/cfn-resource-provider.yaml 

aws cloudformation wait stack-create-complete  --stack-name cfn-certificate-provider 
```

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public-${AWS_REGION}/lambdas/cfn-certificate-provider-0.2.4.zip`.


## Demo
To install the simple sample of the Custom Resource, type:

```sh
read -p "domain name: " DOMAIN_NAME
read -p "hosted zone id: " HOSTED_ZONE
aws cloudformation create-stack --stack-name cfn-certificate-provider-demo \
	--template-body file://cloudformation/demo-stack.yaml \
	--parameters ParameterKey=DomainName,ParameterValue=$DOMAIN_NAME \
		     ParameterKey=HostedZoneId,ParameterValue=$HOSTED_ZONE
aws cloudformation wait stack-create-complete  --stack-name cfn-certificate-provider-demo
```

