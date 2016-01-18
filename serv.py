

import sys
import time
import asyncio


class EchoServerClientProtocol(asyncio.Protocol):

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        # print('Data received: {!r}'.format(message))

        # print('Send: {!r}'.format(message))
        self.transport.write(data[::-1])


loop = asyncio.get_event_loop()

coro = loop.create_server(EchoServerClientProtocol, '127.0.0.1', 9999)
server = loop.run_until_complete(coro)

try:
    loop.run_forever()
except KeyboardInterrupt:
    print('Done')
