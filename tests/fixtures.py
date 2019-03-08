import boto3
import pytest
import uuid

acm = boto3.client("acm")


@pytest.fixture(scope="module")
def certificate():
    name = "test-%s.binx.io" % uuid.uuid4()
    alt_name = "test-%s.binx.io" % uuid.uuid4()
    certificate = acm.request_certificate(
        DomainName=name, ValidationMethod="DNS", SubjectAlternativeNames=[alt_name]
    )
    yield acm.describe_certificate(CertificateArn=certificate["CertificateArn"])[
        "Certificate"
    ]
    acm.delete_certificate(CertificateArn=certificate["CertificateArn"])


@pytest.fixture(scope="module")
def issued_certificate():
    acm.get_paginator("list_certificates")
    result = None
    for response in acm.get_paginator("list_certificates").paginate():
        for certificate in map(
            lambda c: acm.describe_certificate(CertificateArn=c["CertificateArn"]),
            response["CertificateSummaryList"],
        ):
            if certificate["Certificate"]["Status"] == "ISSUED":
                result = certificate["Certificate"]
                break

    assert result, "No issued certificate found in ACM, please add one"
    yield result


@pytest.fixture(scope="module")
def email_certificate():
    name = "test-%s.binx.io" % uuid.uuid4()
    alt_name = "test-%s.binx.io" % uuid.uuid4()
    certificate = acm.request_certificate(
        DomainName=name, ValidationMethod="EMAIL", SubjectAlternativeNames=[alt_name]
    )
    yield acm.describe_certificate(CertificateArn=certificate["CertificateArn"])[
        "Certificate"
    ]
    acm.delete_certificate(CertificateArn=certificate["CertificateArn"])
