import boto3
import pytest
import uuid

from issued_certificate_provider import handler, provider as issued_certificate_provider
from fixtures import certificate, issued_certificate


class Counter(object):

    def __init__(self):
        self.count = 0

    def increment(self, *args, **kwargs):
        self.count += 1


def test_await_pending_completion(certificate):
    counter = Counter()
    issued_certificate_provider.async_reinvoke = counter.increment

    request = Request('Create', certificate['CertificateArn'])
    response = handler(request, ())
    assert counter.count == 1

    request = Request('Update', certificate['CertificateArn'])
    response = handler(request, ())
    assert counter.count == 2

def test_await_completion_issued(issued_certificate):
    counter = Counter()
    issued_certificate_provider.async_reinvoke = counter.increment

    request = Request('Create', issued_certificate['CertificateArn'])
    response = handler(request, ())
    assert response['Status'] == 'SUCCESS', response['Reason']
    assert counter.count == 0



class Request(dict):

    def __init__(self, request_type, certificate_arn, physical_resource_id=None):
        request_id = 'request-%s' % uuid.uuid4()
        self.update({
            'RequestType': request_type,
            'ResponseURL': 'https://httpbin.org/put',
            'StackId': 'arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid',
            'RequestId': request_id,
            'ResourceType': 'Custom::IssuedCertificate',
            'LogicalResourceId': 'Record',
            'ResourceProperties': {
                'CertificateArn': certificate_arn
            }})

        if physical_resource_id:
            self['PhysicalResourceId'] = physical_resource_id