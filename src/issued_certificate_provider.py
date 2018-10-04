import sys
import time

import boto3
import json

from certificate_dns_record_provider import CertificateDNSRecordProvider, PreConditionFailed

acm = boto3.client('acm')
lmbda = boto3.client('lambda')


class IssuedCertificateProvider(CertificateDNSRecordProvider):

    def __init__(self):
        super(IssuedCertificateProvider, self).__init__()
        self.request_schema = {
            "type": "object",
            "required": ["CertificateArn"],
            "properties": {
                "CertificateArn": {
                    "type": "string",
                    "description": "to get the status of"
                }
            }
        }

    def check(self):
        self.physical_resource_id = self.certificate_arn
        try:
            certificate = self.certificate
            if certificate.status == 'ISSUED':
                self.success()
            elif certificate.status == 'PENDING_VALIDATION':
                self.async_reinvoke()
            else:
                self.fail('incorrect certificated status {}, expected ISSUED or PENDING_VALIDATION'.format(
                    certificate.status))
        except PreConditionFailed as error:
            self.fail(error.message)

    def create(self):
        self.check()

    def update(self):
        self.check()

    def delete(self):
        pass

    def async_reinvoke(self, interval_in_seconds=15):
        time.sleep(interval_in_seconds)

        self.increment_attempt()
        payload = json.dumps(self.request).encode('utf-8')
        lmbda.invoke(FunctionName=self.get('ServiceToken'), InvocationType='Event', Payload=payload)

        # exit this lambda, to avoid the framework from sending a CFN response..
        sys.exit(0)

    def attempt(self):
        """ returns the number of attempts waiting for completion """
        return int(self.get('Attempt', 1))

    def increment_attempt(self):
        """ returns the number of attempts waiting for completion """
        self.set('Attempt', self.attempt + 1)


provider = IssuedCertificateProvider()


def handler(request, context):
    return provider.handle(request, context)
