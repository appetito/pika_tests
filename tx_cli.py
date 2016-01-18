import time

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor


class Echo(Protocol):

    def connectionMade(self):
        self.c = 0
        self.start = time.time()
        self.transport.write(b"Hello world!")

    def connectionLost(self, reason):
        print('Stop the event loop', self.c, self.c/(time.time() - self.start))
        reactor.stop()

    def dataReceived(self, data):
        # print('Got', data)
        self.transport.write(data)
        self.c += 1


class EchoClientFactory(ClientFactory):

    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return Echo()

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)


reactor.connectTCP('localhost', 9000, EchoClientFactory())
reactor.run()

