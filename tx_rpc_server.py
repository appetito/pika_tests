
import pika

from pika.adapters import twisted_connection
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor, protocol


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
def server():
    conn = yield make_connection()
    chan = yield conn.channel()
    print('Channel', chan)
    yield chan.queue_declare(queue='rpc_queue')
    queue, ctag = yield chan.basic_consume(queue='rpc_queue', no_ack=True)

    while True:
        ch, method, props, body = yield queue.get()
        # print('Get', body, props)
        yield chan.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            body=body[::-1])


reactor.callWhenRunning(server)
reactor.run()
print('Done')
