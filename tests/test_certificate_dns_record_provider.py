import uuid

from provider import handler
from fixtures import certificate, email_certificate


def test_retrieval_of_dns_record(certificate):
    request = Request("Create", certificate["CertificateArn"])
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "Name" in response["Data"]
    assert "Type" in response["Data"]
    assert "Value" in response["Data"]
    assert response["Data"]["Type"] == "CNAME"
    assert "PhysicalResourceId" in response
    record_name = response["Data"]["Name"]
    physical_resource_id = response["PhysicalResourceId"]
    assert physical_resource_id == record_name

    request = Request(
        "Create",
        certificate["CertificateArn"],
        certificate["SubjectAlternativeNames"][1],
    )
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "Name" in response["Data"]
    assert "Type" in response["Data"]
    assert "Value" in response["Data"]
    assert response["Data"]["Type"] == "CNAME"
    assert "PhysicalResourceId" in response
    assert record_name != response["Data"]["Name"]
    assert physical_resource_id != response["PhysicalResourceId"]


def test_retrieval_of_dns_record_via_update(certificate):
    request = Request("Update", certificate["CertificateArn"])
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "Name" in response["Data"]
    assert "Type" in response["Data"]
    assert "Value" in response["Data"]
    assert response["Data"]["Type"] == "CNAME"
    assert "PhysicalResourceId" in response
    assert response["PhysicalResourceId"] == response["Data"]["Name"]


def test_retrieval_of_non_existing_domain_name(certificate):
    request = Request("Update", certificate["CertificateArn"])
    request["ResourceProperties"]["DomainName"] = "nonexisting.domain.name"
    response = handler(request, {})
    assert response["Status"] == "FAILED", response["Reason"]
    assert response["Reason"].startswith("No validation option found for domain")


def test_retrieval_non_existing_certificate():
    request = Request(
        "Create",
        "arn:aws:acm:eu-central-1:111111111111:certificate/ffffffff-ffff-ffff-ffff-ffffffffffff",
    )
    response = handler(request, {})
    assert response["Status"] == "FAILED", response["Reason"]
    assert "ResourceNotFoundException" in response["Reason"]


def test_create_incorrect_validation_method(email_certificate):
    request = Request("Create", email_certificate["CertificateArn"])
    response = handler(request, {})
    assert response["Status"] == "FAILED", response["Reason"]
    assert response["Reason"].startswith("domain is using validation method")


class Request(dict):
    def __init__(
        self, request_type, certificate_arn, domain_name=None, physical_resource_id=None
    ):
        request_id = "request-%s" % uuid.uuid4()
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": request_id,
                "ResourceType": "Custom::CertificateDNSRecord",
                "LogicalResourceId": "Record",
                "ResourceProperties": {"CertificateArn": certificate_arn},
            }
        )

        if domain_name:
            self["ResourceProperties"]["DomainName"] = domain_name

        if physical_resource_id:
            self["PhysicalResourceId"] = physical_resource_id
