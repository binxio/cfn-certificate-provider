import certificate_dns_record_provider
import certificate_provider
import issued_certificate_provider


def handler(request, context):
    if request['ResourceType'] == 'Custom::Certificate':
        return certificate_provider.handler(request, context)
    elif request['ResourceType'] == 'Custom::IssuedCertificate':
        return issued_certificate_provider.handler(request, context)
    else:
        return certificate_dns_record_provider.handler(request, context)

