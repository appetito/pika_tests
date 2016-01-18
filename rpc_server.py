

import sys
import time
import asyncio
import pika

from pika.adapters import asyncio_connection


@asyncio.coroutine
def make_connection(loop, host="localhost", port=5672):

    def connection_factory():
        params = pika.ConnectionParameters()
        return asyncio_connection.AsyncioProtocolConnection(params, loop=loop)

    transport, connection = yield from loop.create_connection(connection_factory, host, port)
    yield from connection.ready
    return connection


@asyncio.coroutine
def server(loop):
    conn = yield from make_connection(loop)
    chan = yield from conn.channel()

    conn2 = yield from make_connection(loop)
    chan2 = yield from conn2.channel()
    print('Channel', chan)
    yield from chan.queue_declare(queue='rpc_queue')
    queue, ctag = yield from chan.basic_consume(queue='rpc_queue', no_ack=True)

    while True:
        ch, method, props, body = yield from queue.get()
        # print('Get', body, props)
        yield from chan2.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            body=body[::-1])


loop = asyncio.get_event_loop()

try:
    task = asyncio.ensure_future(server(loop))
    loop.run_until_complete(task)
except KeyboardInterrupt:
    print('Done')
