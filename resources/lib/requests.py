import gzip
import json as real_json
from kodi_six.utils import py2_encode, py2_decode

try:
    from io import BytesIO as StringIO
    from urllib.response import addinfourl
    from urllib.parse import quote, urlencode
    from urllib.request import HTTPDefaultErrorHandler, HTTPRedirectHandler, HTTPSHandler, build_opener, Request
    from urllib.error import HTTPError
except:
    from StringIO import StringIO
    from urllib import addinfourl, quote, urlencode
    from urllib2 import HTTPDefaultErrorHandler, HTTPRedirectHandler, HTTPSHandler, build_opener, Request, HTTPError

__author__ = 'bromix'  # with small modifications by PUR3


class ErrorHandler(HTTPDefaultErrorHandler):


    def http_error_default(self, req, fp, code, msg, hdrs):
        infourl = addinfourl(fp, hdrs, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl


class NoRedirectHandler(HTTPRedirectHandler):


    def http_error_302(self, req, fp, code, msg, headers):
        infourl = addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl


    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


class Response:


    def __init__(self):
        self.headers = {}
        self.code = -1
        self.text = u''
        self.status_code = -1


    def read(self):
        return self.text


    def json(self):
        return real_json.loads(self.text)


def _request(method, url,
             params=None,
             data=None,
             headers=None,
             cookies=None,
             files=None,
             auth=None,
             timeout=None,
             allow_redirects=False,
             proxies=None,
             hooks=None,
             stream=None,
             verify=None,
             cert=None,
             json=None):
    if not headers:
        headers = {}

    url = quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    handlers = []

    # starting with python 2.7.9 urllib verifies every https request
    if False is verify:
        import sys
        if sys.version_info >= (2, 7, 9):
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            handlers.append(HTTPSHandler(context=ssl_context))

    # handlers.append(HTTPCookieProcessor())
    # handlers.append(ErrorHandler)
    if not allow_redirects:
        handlers.append(NoRedirectHandler)
    opener = build_opener(*handlers)
    opener.addheaders = []  # Removes default User-Agent

    query = ''
    if params:
        for key in params:
            value = params[key]
            if isinstance(value, str):
                value = py2_decode(value)
            params[key] = py2_encode(value)
        query = urlencode(params)
    if query:
        url += '?' + query
    request = Request(url)
    if headers:
        for key in headers:
            request.add_header(key, str(py2_encode(headers[key])))
    if data or json:
        if headers.get('Content-Type', '').startswith('application/x-www-form-urlencoded') or data:
            # transform a string into a map of values
            if isinstance(data, basestring):
                _data = data.split('&')
                data = {}
                for item in _data:
                    name, value = item.split('=')
                    data[name] = value

            # encode each value
            for key in data:
                data[key] = data[key]
                if isinstance(data[key], unicode):
                    data[key] = py2_encode(data[key])

            # urlencode
            request.data = urlencode(data)
        elif headers.get('Content-Type', '').startswith('application/json') and data:
            request.data = py2_encode(real_json.dumps(data))
        elif json:
            request.data = py2_encode(real_json.dumps(json))
        else:
            if not isinstance(data, basestring):
                data = str(data)

            if isinstance(data, str):
                data = py2_encode(data)
                pass
            request.data = data
    elif method.upper() in ('POST', 'PUT'):
        request.data = 'null'
    request.get_method = lambda: method
    result = Response()
    response = None
    try:
        response = opener.open(request, timeout=timeout)
    except HTTPError as e:
        # HTTPError implements addinfourl, so we can use the exception to construct a response
        if isinstance(e, addinfourl):
            response = e

    # process response
    result.headers.update(response.headers)
    result.status_code = response.getcode()
    if response.headers.get('Content-Encoding', '').startswith('gzip'):
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        result.text = f.read()
    elif stream:
        return result
    else:
        result.text = response.read()
    return result


def get(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return _request('GET', url, **kwargs)


def post(url, data=None, json=None, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return _request('POST', url, data=data, json=json, **kwargs)


def put(url, data=None, json=None, **kwargs):
    return _request('PUT', url, data=data, json=json, **kwargs)


def delete(url, **kwargs):
    return _request('DELETE', url, **kwargs)


def head(url, **kwargs):
    return _request('HEAD', url, **kwargs)