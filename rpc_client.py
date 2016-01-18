

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


@asyncio.coroutine
def make_connection(loop, host="localhost", port=5672):

    def connection_factory():
        params = pika.ConnectionParameters()
        return asyncio_connection.AsyncioProtocolConnection(params, loop=loop)

    transport, connection = yield from loop.create_connection(connection_factory, host, port)
    yield from connection.ready
    return connection


@asyncio.coroutine
def call(loop):
    global c
    conn = yield from make_connection(loop)
    chan = yield from conn.channel()

    conn2 = yield from make_connection(loop)
    chan2 = yield from conn2.channel()
    print('Channel', chan)
    result = yield from chan2.queue_declare(exclusive=True)
    cb_queue = result.method.queue
    print('CBQ', cb_queue, result)
    # asyncio.ensure_future(work(loop, chan))
    queue, ctag = yield from chan2.basic_consume(queue=cb_queue, no_ack=True)


    c.reset()

    while True:
        yield from chan.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                 reply_to=cb_queue,
                 ),
            body='Hello World!')

        ch, method, props, body = yield from queue.get()
        # print('Get reply', body)
        c.inc()


loop = asyncio.get_event_loop()

try:
    task = asyncio.ensure_future(call(loop))
    loop.run_until_complete(task)
except KeyboardInterrupt:
    print('Done', c)
