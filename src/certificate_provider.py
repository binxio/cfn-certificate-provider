import sys
import time

import boto3
import json
import logging
from botocore.exceptions import ClientError
from cfn_resource_provider import ResourceProvider

logger = logging.getLogger()


class CertificateProvider(ResourceProvider):
    """
    A Custom CertificateManager Certificate provider for use with DNS validation
    which returns immediately after the certificate request is created.

    Using the custom CertificateDNSRecord you can retrieve the
    DNS record to be created.

    The CertificateIssued provider can be used to wait until
    the certificate has actually been issued.
    """

    def __init__(self):
        super(CertificateProvider, self).__init__()
        self.request_schema = {
            "type": "object",
            "required": ["DomainName", "ValidationMethod"],
            "additionalProperties": True,
            "properties": {
                "DomainName": {"type": "string", "description": "to create"},
                "ValidationMethod": {
                    "type": "string",
                    "enum": ["DNS"],
                    "description": "to get the DNS validation record for",
                },
            },
        }

    def create(self):
        try:
            self.request_certificate()
        except ClientError as error:
            self.fail("{}".format(error))
            self.physical_resource_id = "failed-to-create"

    def request_certificate(self):
        arguments = self.properties.copy()
        region = arguments.pop("Region", None)
        acm = boto3.client("acm", region_name=region)
        if "ServiceToken" in arguments:
            del arguments["ServiceToken"]

        if "IdempotencyToken" not in arguments:
            arguments["IdempotencyToken"] = self.request["LogicalResourceId"]
        response = acm.request_certificate(**arguments)
        self.physical_resource_id = response["CertificateArn"]

    def update(self):
        new_names = set(self.properties.keys())
        old_names = (
            set(self.old_properties.keys())
            if "OldResourceProperties" in self.request
            else new_names
        )

        changed_properties = list(new_names.symmetric_difference(old_names))
        for name in new_names.union(old_names).difference(set(["ServiceToken"])):
            if self.get(name, None) != self.get_old(name, self.get(name)):
                changed_properties.append(name)

        try:
            if "DomainName" in changed_properties:
                return self.request_certificate()
            elif (
                changed_properties
                and len(changed_properties) == 1
                and changed_properties[0] == "Options"
            ):
                try:
                    region = self.properties.get("Region")
                    acm = boto3.client("acm", region_name=region)
                    acm.update_certificate_options(
                        CertificateArn=self.physical_resource_id,
                        Options=self.get("Options"),
                    )
                except ClientError as error:
                    self.fail("{}".format(error))
            elif changed_properties:
                self.fail(
                    'You can only change the "Options" and "DomainName" '
                    + "of a certificate, you tried to change {}".format(
                        ", ".join(changed_properties)
                    )
                )
            else:
                self.success("nothing to change")
        except ClientError as error:
            self.fail("{}".format(error))

    def delete(self):
        if not self.physical_resource_id or not self.physical_resource_id.startswith(
            "arn:aws:acm:"
        ):
            return

        try:
            region = self.properties.get("Region")
            acm = boto3.client("acm", region_name=region)
            response = acm.delete_certificate(CertificateArn=self.physical_resource_id)
        except ClientError as error:
            self.success("Ignore failure to delete certificate {}".format(error))


provider = CertificateProvider()


def handler(request, context):
    return provider.handle(request, context)
