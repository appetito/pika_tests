import asyncio
import time

class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop
        self.c = 0

    def connection_made(self, transport):
        self.transport = transport
        self.start = time.time()
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        # print('Data received: {!r}'.format(data.decode()))
        self.transport.write(self.message.encode())
        self.c += 1

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop', self.c, self.c/(time.time() - self.start))
        self.loop.stop()

loop = asyncio.get_event_loop()
message = 'Hello World!'
coro = loop.create_connection(lambda: EchoClientProtocol(message, loop),
                              '127.0.0.1', 9999)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()