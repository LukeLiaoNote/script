# 根据header响应s3源或者自定义源
def lambda_handler(event, context):
    request = event['Records'][0]['cf']['request']
    viewerCountry = request['headers'].get('cloudfront-viewer-country')
    vieweruseragent = request['headers'].get('user-agent')[0]['value']
    vieweruseragent = vieweruseragent.lower()

    seo_list = ['googlebot','bingbot','twitterbot','linkedinbot','mediapartners-google','naverbot','yeti']
    isBoot = any(vieweruseragent.find(i)!=-1 for i in seo_list)

    if viewerCountry[0]['value'] == 'CN':
        domainName = 'example.s3.amazonaws.com'
        request['origin']['s3']['domainName'] = domainName
        request['headers']['host'] = [{'key': 'host', 'value': domainName}]
    elif isBoot:
        domainName = 'example.com'
        request['origin'] = {
            'custom': {
                'domainName': domainName,
                'port': 443,
                'protocol': 'https',
                'path': '',
                'sslProtocols': ['TLSv1'],
                'readTimeout': 5,
                'keepaliveTimeout': 5,
                'customHeaders': {}
            }
        }
        request['headers']['host'] = [{'key': 'host', 'value': domainName}]
    return request