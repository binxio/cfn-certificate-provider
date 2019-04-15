import boto3
import pytest
import uuid
from botocore.exceptions import ClientError

from certificate_provider import handler

acm = boto3.client("acm")


@pytest.fixture(scope="module")
def certificates():
    arns = []
    yield arns
    for arn in arns:
        try:
            acm.delete_certificate(CertificateArn=arn)
        except ClientError as e:
            pass


def test_create_wildcard(certificates):
    name = "test-%s.binx.io" % uuid.uuid4()

    request = Request("Create", f'*.{name}')
    request["ResourceProperties"]["DomainValidationOptions"] = [
      { 'DomainName': f'*.{name}', 'ValidationDomain': name }
    ]
    response = handler(request, ())
    assert response["Status"] == "SUCCESS", response["Reason"]
    physical_resource_id = response["PhysicalResourceId"]
    certificates.append(physical_resource_id)

def test_create(certificates):
    name = "test-%s.binx.io" % uuid.uuid4()
    new_name = "test-new-%s.binx.io" % uuid.uuid4()
    alt_name = "test-%s.binx.io" % uuid.uuid4()

    request = Request("Create", name)
    request["ResourceProperties"]["SubjectAlternativeNames"] = [alt_name]
    response = handler(request, ())
    assert response["Status"] == "SUCCESS", response["Reason"]
    physical_resource_id = response["PhysicalResourceId"]
    certificates.append(physical_resource_id)

    request["RequestType"] = "Update"
    request["PhysicalResourceId"] = physical_resource_id
    response = handler(request, ())
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert response["Reason"] == "nothing to change"
    assert physical_resource_id == response["PhysicalResourceId"]

    request["OldResourceProperties"] = request["ResourceProperties"].copy()
    request["ResourceProperties"]["DomainName"] = new_name
    response = handler(request, ())
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert physical_resource_id != response["PhysicalResourceId"]

    request["OldResourceProperties"] = request["ResourceProperties"].copy()
    request["ResourceProperties"]["SubjectAlternativeNames"] = ["new-" + alt_name]
    response = handler(request, ())
    assert response["Status"] == "FAILED", response["Reason"]
    assert response["Reason"].startswith(
        'You can only change the "Options" and "DomainName" of a certificate,'
    ), response["Reason"]

    request["ResourceProperties"]["SubjectAlternativeNames"] = [alt_name]
    request["ResourceProperties"]["Options"] = {
        "CertificateTransparencyLoggingPreference": "DISABLED"
    }
    response = handler(request, ())
    assert response["Status"] == "FAILED", response["Reason"]
    assert response["Reason"].startswith(
        "An error occurred (InvalidStateException) when calling the UpdateCertificateOptions operation"
    )

    request["RequestType"] = "Delete"
    response = handler(request, ())
    assert response["Status"] == "SUCCESS", response["Reason"]
    try:
        acm.delete_certificate(CertificateArn=physical_resource_id)
        assert False, "Delete operation failed for {}".format(physical_resource_id)
    except acm.exceptions.ResourceNotFoundException:
        pass


class Request(dict):
    def __init__(self, request_type, domain_name, physical_resource_id=None):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": "Custom::Certificate",
                "LogicalResourceId": "Record",
                "ResourceProperties": {
                    "DomainName": domain_name,
                    "ValidationMethod": "DNS",
                },
            }
        )

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id
