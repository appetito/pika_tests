

import sys
import time
import asyncio
import pika

from pika.adapters import asyncio_connection


class Counter:

    def __init__(self, name=''):
        self.start = time.time()
        self.cnt = 0
        self.name = name

    def reset(self):
        self.start = time.time()
        self.cnt = 0

    def inc(self, value=1):
        self.cnt += value

    def summary(self):
        now = time.time()
        return {
            'time': now - self.start,
            'count': self.cnt,
            'rate': self.cnt / (now - self.start)
        }

    def __str__(self):
        return '{name}: time: {time}, count: {count}, rate: {rate}'.format(
            name=self.name, **self.summary())


c = Counter('Counter')
cn = None

@asyncio.coroutine
def make_connection(loop, host="localhost", port=5672):

    def connection_factory():
        params = pika.ConnectionParameters()
        return asyncio_connection.AsyncioProtocolConnection(params, loop=loop)

    transport, connection = yield from loop.create_connection(connection_factory, host, port)
    yield from connection.ready
    return connection


@asyncio.coroutine
def tick():
    while True:
        print(c)
        yield from asyncio.sleep(1)


@asyncio.coroutine
def work(loop, chan):
    while True:
        yield from chan.basic_publish(
            exchange='',
            routing_key='testq',
            body='Hello World!')
        c.inc()


@asyncio.coroutine
def push(loop):
    global cn
    conn = yield from make_connection(loop)
    chan = yield from conn.channel()
    cn = conn
    print('Channel', chan)
    c.reset()
    # asyncio.ensure_future(work(loop, chan))
    while True:
        yield from chan.basic_publish(
            exchange='',
            routing_key='testq',
            body='Hello World!')
        c.inc()

loop = asyncio.get_event_loop()

try:
    task = asyncio.ensure_future(push(loop))
    loop.run_until_complete(task)
    print('Done')
except KeyboardInterrupt:
    print(c)