

import sys
import time
import pika

from pika.adapters import twisted_connection
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor, protocol, task


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


@inlineCallbacks
def make_connection(host="localhost", port=5672):
    params = pika.ConnectionParameters()
    cc = protocol.ClientCreator(
        reactor,
        twisted_connection.TwistedProtocolConnection,
        params)
    connection = yield cc.connectTCP(host, port)
    yield connection.ready
    return connection


@inlineCallbacks
def call():
    global c
    conn = yield make_connection()
    chan = yield conn.channel()
    print('Channel', chan)
    result = yield chan.queue_declare(exclusive=True)
    cb_queue = result.method.queue
    print('CBQ', cb_queue, result)
    # asyncio.ensure_future(work(loop, chan))
    queue, ctag = yield chan.basic_consume(queue=cb_queue, no_ack=True)

    c.reset()

    while True:
        yield chan.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                 reply_to=cb_queue,
                 ),
            body='Hello World!')

        ch, method, props, body = yield queue.get()
        # print('Get reply', body)
        c.inc()


reactor.callWhenRunning(call)
reactor.run()
print('Done', c)
