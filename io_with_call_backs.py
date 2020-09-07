import socket
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

from utils import parse_response

selector = DefaultSelector()

url_todo = {['/']}
url_seen = {['/']}


class Fetcher:
    def __init__(self, url):
        self.response = r''
        self.url = url
        self.sock = None
        self.get_links = parse_response

    def fetch(self):
        self.sock = socket.socket()
        self.sock.setblocking(False)

        try:
            self.sock.connect(self.url)  # keep executing as this is non-blocking
        except BlockingIOError:
            pass

        selector.register(self.sock.fileno(), EVENT_WRITE, self.connected)

    def connected(self, key, mask):
        print('Connected!')
        selector.unregister(key.fd)
        request = f'GET {self.url} HTTP/1.0\r\n Host: xkcd.com\r\n\r\n'
        encoded = request.encode('ascii')

        self.sock.send(encoded)  # keep executing as this is non-blocking

        selector.register(key.fd,
                          EVENT_READ,  # The callback is executed each time the selector sees that the socket is
                          # "readable", which could mean two things: the socket has data or it is closed.
                          self.read_response)

    def read_response(self, key, mask):
        global STOPPED

        chunk = self.sock.recv(4096)
        if chunk:
            self.response += chunk
        else:
            selector.unregister(key.fd)  # Done reading. Until now `the_loop` was executing this function
            # when it saw that self.socket is "readable".

            links = self.get_links(self.response)

            for link in links.difference(url_seen):
                url_todo.add(link)
                Fetcher(link).fetch()

            url_seen.update(links)
            url_todo.remove(self.url)

            if not url_todo:
                STOPPED = True


STOPPED = False


def the_loop():
    while not STOPPED:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)


if __name__ == '__main__':
    new_fetcher = Fetcher('www.xkcd.com')
    new_fetcher.fetch()

    the_loop()
