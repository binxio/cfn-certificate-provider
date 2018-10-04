# Custom Certificate Provider with DNS validation support
A CloudFormation custom resource provider for creating Certificates using DNS validation.

It will work using three Custom Resources: 

1. Custom::Certificate to request a certificate without waiting for it to be issued
2. Custom::IssuedCertificate which will activately wait until the certificate is issued
3. Custom::CertificateDNSRecord which will obtain the DNS record for a domain.

