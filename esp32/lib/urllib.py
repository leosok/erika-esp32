
"""Open an arbitrary URL.

Adapted for Micropython by Alex Cowan <acowan@gmail.com>

Includes some elements from the original urllib and urlencode libraries for Python
"""

import usocket as socket
import ussl as ssl

class URLOpener:
    def __init__(self, url, post_data={}):
        self.code = 0
        self.headers = {}
        self.body = ""
        self.url = url
        [scheme, host, path, data] = urlparse(self.url)
        if scheme == 'http':
            addr = socket.getaddrinfo(host, 80)[0][-1]
            s = socket.socket()
            s.settimeout(5)
            s.connect(addr)
        else:
            sock = socket.socket()
            sock.settimeout(5)
            sock.connect(socket.getaddrinfo(host, 443)[0][4])
            s = ssl.wrap_socket(sock)

        if post_data:
            data = urlencode(post_data)
            #print('POST %s HTTP/1.0\r\nHost: %s\r\n\r\n%s\r\n' % (path or '/', host, data.strip()))
            s.write(b'POST %s HTTP/1.0\r\nHost: %s\r\n\r\n%s\r\n' % (path or '/', host, data.strip()))
        else:
            #print('GET %s%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path or '/', '?'+data.strip(), host))
            s.write(b'GET %s%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path or '/', '?'+data.strip(), host))
        while 1:
            recv = s.read(1024)
            if len(recv) == 0: break
            self.body += recv.decode()
        print(self.body)
        s.close()
        self._parse_result()

    def read(self):
        return self.body

    def _parse_result(self):
        self.body = self.body.split('\r\n')
        while self.body:
            line = self.body.pop(0).strip()
            if line == '':
                 break
            if line[0:4] == 'HTTP':
                data = line.split(' ')
                self.code = int(data[1])
                continue
            if len(line.split(':')) >= 2:
                data = line.split(':')
                self.headers[data[0]] = (':'.join(data[1:])).strip()
                continue
        self.body = '\r\n'.join(self.body)
    	return

def urlparse(url):
    scheme = url.split('://')[0].lower()
    url = url.split('://')[1]
    host = url.split('/')[0]
    path = '/'
    data = ""
    if host != url:
        path = ''.join(url.split('/')[1:])
        if path.count('?'):
            if path.count('?') > 1:
                raise Exception('URL malformed, too many ?')
            [path, data] = path.split('?')
    return [scheme, host, path, data]

def urlopen(url, data=None, method="GET"):
    if data is not None and method == "GET":
        method = "POST"
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]

    s = usocket.socket(ai[0], ai[1], ai[2])
    try:
        s.connect(ai[-1])
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)

        s.write(method)
        s.write(b" /")
        s.write(path)
        s.write(b" HTTP/1.0\r\nHost: ")
        s.write(host)
        s.write(b"\r\n")

        if data:
            s.write(b"Content-Length: ")
            s.write(str(len(data)))
            s.write(b"\r\n")
        s.write(b"\r\n")
        if data:
            s.write(data)

        l = s.readline()
        l = l.split(None, 2)
        #print(l)
        status = int(l[1])
        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break
            #print(l)
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
            elif l.startswith(b"Location:"):
                raise NotImplementedError("Redirects not yet supported")
    except OSError:
        s.close()
        raise

    return s

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')

def quote(s):
    res = []
    replacements = {}
    for c in s:
        if c in always_safe:
            res.append(c)
            continue
        res.append('%%%x' % ord(c))
    return ''.join(res)

def quote_plus(s):
    if ' ' in s:
        s = s.replace(' ', '+')
    return quote(s)

def unquote(s):
    """Kindly rewritten by Damien from Micropython"""
    """No longer uses caching because of memory limitations"""
    res = s.split('%')
    for i in range(1, len(res)):
        item = res[i]
        try:
            res[i] = chr(int(item[:2], 16)) + item[2:]
        except ValueError:
            res[i] = '%' + item
    return "".join(res)

def unquote_plus(s):
    """unquote('%7e/abc+def') -> '~/abc def'"""
    s = s.replace('+', ' ')
    return unquote(s)

def urlencode(query):
    if isinstance(query, dict):
        query = query.items()
    l = []
    for k, v in query:
        k = quote_plus(str(k))
        v = quote_plus(str(v))
        l.append(k + '=' + v)
    return '&'.join(l)
