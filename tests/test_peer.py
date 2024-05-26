import time
from unittest import TestCase
import Pyro4
import Pyro4.errors

from net.peer import Peer


class TestPeer(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.peer_host = Peer('host')
        cls.peer_1 = Peer('peer-1')
        cls.lobby_proxy = Pyro4.Proxy('PYRONAME:lobby')

    def test_new_lobby(self):
        self.peer_host.new_lobby()
        self.assertIn('host', self.lobby_proxy.list_players())
        Pyro4.Proxy('PYRONAME:lobby')
        self.lobby_proxy.join_lobby("player1", "PYRO:player1@localhost:12345")

    def test_shutdown_lobby(self):
        self.peer_host.new_lobby()
        self.lobby_proxy.join_lobby("player1", "PYRO:player1@localhost:12345")
        self.peer_host.shutdown_lobby()
        with self.assertRaises(Pyro4.errors.ConnectionClosedError):
            self.lobby_proxy.join_lobby("player2", "PYRO:player2@localhost:12345")

    def test_connect_to_lobby(self):
        self.peer_host.new_lobby()
        self.assertTrue(self.peer_1.connect_to_lobby())
        print(self.lobby_proxy.list_players())
