# coding: utf-8
from twisted.internet import reactor

from twisted.internet.protocol import ServerFactory, connectionDone

from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionMade(self):

        self.sendLine("Enter your login as 'login: your login'".encode())

    def connectionLost(self, reason=connectionDone):

        self.factory.clients.remove(self)

        for user in self.factory.clients:
            user.sendLine(f"{self.login} left the chat.".encode())

    def send_history(self):
        """
        Returns the last 10 messages to chat.
        """
        for message in self.factory.last_mess:
            self.sendLine(message.encode())

    def send_mess(self, message):
        """
        Sending messages to all clients except self.
        """
        for user in self.factory.clients:
            if user is not self:
                user.sendLine(message.encode())

    def check_login(self, login):
        """
        Checking for the uniqueness of a login.

            :param login: users login
            :return: is the login unique?
        """
        for user in self.factory.clients:
            if user is not self:
                if user.login == login:
                    self.sendLine(f"Login {login} is already taken. Please use different one.".encode())
                    return False
        return True

    def lineReceived(self, line: bytes):

        content = line.decode()

        if self.login is not None:

            content = f"{self.login}: {content}"
            self.factory.add_mess = content
            self.send_mess(content)

        else:

            # login:admin -> admin

            if content.startswith("login:"):

                log = content.replace("login: ", "")
                if self.check_login(log):
                    self.login = log
                    self.factory.clients.append(self)
                    self.sendLine(f"Welcome, {self.login}!".encode())
                    self.send_history()
                    self.send_mess(f"{self.login} joined the chat.")

            else:
                self.sendLine("Invalid login".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    _last_10_mess: list

    def startFactory(self):
        self.clients = []
        self._last_10_mess = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")

    @property
    def last_mess(self):
        return self._last_10_mess

    @last_mess.setter
    def add_mess(self, mess):
        if len(self._last_10_mess) >= 10:
            del self._last_10_mess[0]
        self._last_10_mess.append(mess)


reactor.listenTCP(1234, Server())
reactor.run()
