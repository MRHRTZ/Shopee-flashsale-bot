import json

from urllib import parse
from seleniumwire.utils import decode

def decode_network(request):
    return json.loads(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')))

def is_valid_url(url):
    try:
        result = parse.urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False