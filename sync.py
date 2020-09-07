import socket

from utils import parse_response

q = set()


def fetch_blocking(url):
    """ Socket operations are blocking by default. When the thread calls `connect` or `recv` it pouses until
     the operation is complete. To download many pages we need many threads. """

    sock = socket.socket()
    sock.connect(('xkcd.com', 80))
    request = f'GET {url} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'
    sock.send(request.encode('asci'))

    response = b''

    chunk = sock.recv(4096)
    while chunk:
        response += chunk
        chunk = sock.recv(4096)

    links = parse_response(response)
    q.add(links)
