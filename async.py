import socket

from utils import parse_response

q = set()


def fetch_non_blocking(url):
    """ Non-blocking socket with brute force send() to try if the connection was established. """

    sock = socket.socket()
    sock.setblocking(False)

    try:
        sock.connect(('xkcd.com', 80))
    except BlockingIOError:  # this is actually good behaviour but they throw this error
        pass

    request = f'GET {url} HTTP/1.0\r\nHost: xkcd.com\r\n\r\n'
    encoded = request.encode('asci')

    while True:
        # Needs a way to know when the connection is established, so it can send the HTTP request.
        # We could simply keep trying in a tight loop, but it cannot efficiently await events on multiple sockets
        try:
            sock.send(encoded)
            break
        except OSError as e:
            pass
    print('sent')

    response = b''

    chunk = sock.recv(4096)
    while chunk:
        response += chunk
        chunk = sock.recv(4096)

    links = parse_response(response)
    q.add(links)
