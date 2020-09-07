import socket
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

from utils import parse_response

selector = DefaultSelector()


class Task:
    def __init__(self, coro):
        self.coro = coro
        self.step(Future())  # Initiate fetch(), This initial Future() is just to pass None but in Future.result attr

    def step(self, future):
        try:
            next_future: Future = self.coro.send(future.result)  # advance the fetch() with next result
            # as this future comes from within fetch(). It will get back here on every `yield` in self.coro
        except StopIteration:
            return

        next_future.add_done_callback(self.step)  # When this new feature resolves it will call this added self.step


class Future:
    """ This future has many deficiencies. For example, once this future is resolved, a coroutine that yields
    it should resume immediately instead of pausing. """

    def __init__(self):
        self.result = None
        self._callbacks = []

    def __iter__(self):
        yield self  # pauses here
        return self.result  # returns on the second next() call which will be from `yield from` in our case

    def add_done_callback(self, fn):
        self._callbacks.append(fn)

    def set_result(self, result):
        """ It is "resolved" by a call to set_result. """
        self.result = result

        for fn in self._callbacks:
            fn(self)


class Fetcher:
    def __init__(self, url):
        self.response = r''
        self.url = url
        self.sock = None
        self.get_links = parse_response

    def fetch(self):
        """ Coroutine of interest. """

        self.sock = socket.socket()
        self.sock.setblocking(False)

        try:
            self.sock.connect(('xkcd.com', 80))
        except BlockingIOError:
            pass

        connected = Future()  # create a pending future

        def on_connect():
            """ Advances the fetch() - by resolving the Future which calls Task.step() that calls fetch() """
            connected.set_result(
                True)  # `connected` Feature has previous Task.step() in self._callback
            # those callback are called in set_result()

        selector.register(  # register to call on_connect() once the write event happens
            self.sock.fileno(),
            EVENT_WRITE,
            on_connect)

        yield from connected  # yield it to pause fetch until the socket is ready
        print("Connected.")

        selector.unregister(self.sock.fileno())

        request = f'GET {self.url} HTTP/1.0\r\n Host: xkcd.com\r\n\r\n'
        encoded = request.encode('ascii')
        self.sock.send(encoded)

        self.response = yield from read_all(self.sock)
        print(self.response)
        global STOPPED
        STOPPED = True


def read_all(sock):
    response = []
    chunk = yield from read(sock)

    while chunk:
        response.append(chunk)
        chunk = yield from read(sock)

    return b''.join(response)


def read(sock):
    chunk_or_none = Future()

    def on_read():
        chunk_or_none.set_result(sock.recv(4096))

    selector.register(
        sock.fileno(),
        EVENT_READ,
        on_read)
    chunk = yield from chunk_or_none
    selector.unregister(sock.fileno())
    return chunk


STOPPED = False  # we will stop after first response


def the_loop():
    while not STOPPED:
        events = selector.select()  # Get all events registered on selector that are ready.
        for event_key, event_mask in events:
            callback = event_key.data  # Function to be called when the event happens
            callback()
    print('Done')


fetcher = Fetcher('/353/')  # Set up Fetcher
Task(fetcher.fetch())  # Initiate fetch()

the_loop()  # we will stay there until all fetches are done (STOPPED = True)
