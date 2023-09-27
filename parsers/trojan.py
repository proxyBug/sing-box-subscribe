import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    _netloc = server_info.netloc.split("@")
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    node = {
        'tag': unquote(server_info.fragment),
        'type': 'trojan',
        'server': re.sub(r"\[|\]", "", _netloc[1].rsplit(":", 1)[0]),
        'server_port': int(_netloc[1].rsplit(":", 1)[1]),
        'password': _netloc[0],
        'tls': {
            'enabled': True
        }
    }
    if netquery.get('allowInsecure') and netquery['allowInsecure'] == '1' :
        node['tls']['insecure'] = True
    if netquery.get('alpn'):
        node['tls']['alpn'] = netquery.get('alpn').strip('{}').split(',')
    if netquery.get('sni'):
        node['tls']['server_name'] = netquery.get('sni', '')
    if netquery.get('fp'):
        node['tls']['utls'] = {
            'enabled': True,
            'fingerprint': netquery.get('fp')
        }
    if netquery.get('type'):
        if netquery['type'] == 'h2':
            node['transport'] = {
                'type':'http',
                'host':netquery.get('host', node['server']),
                'path':netquery.get('path', '/')
            }
        if netquery['type'] == 'ws':
            node['transport'] = {
                'type':'ws',
                'path':netquery.get('path', '/')
            }
            if netquery.get('host'):
                node['transport']['headers']['Host'] = netquery['host']
        if netquery['type'] == 'grpc':
            node['transport'] = {
                'type':'grpc',
                'service_name':netquery.get('serviceName', '')
            }
    return node
