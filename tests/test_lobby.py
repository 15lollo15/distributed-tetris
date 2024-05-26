from unittest import TestCase

import Pyro4
import threading
import time

from net.lobby import Lobby


class TestGameLobby(TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the test server in a separate thread
        def start_server():
            daemon = Pyro4.Daemon()
            ns = Pyro4.locateNS()
            uri = daemon.register(Lobby(3))
            ns.register("example.gamelobby", uri)
            daemon.requestLoop()

        cls.server_thread = threading.Thread(target=start_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Give the server some time to start

        cls.lobby = Pyro4.Proxy("PYRONAME:example.gamelobby")

    @classmethod
    def tearDownClass(cls):
        cls.lobby._pyroRelease()

    def test_join_lobby(self):
        response = self.lobby.join_lobby("player1", "PYRO:player1@localhost:12345")
        self.assertTrue(response)
        response = self.lobby.join_lobby("player1", "PYRO:player1@localhost:12345")
        self.assertFalse(response)

    def test_leave_lobby(self):
        self.lobby.join_lobby("player2", "PYRO:player2@localhost:12345")
        response = self.lobby.leave_lobby("player2")
        self.assertTrue(response)
        response = self.lobby.leave_lobby("player2")
        self.assertFalse(response)

    def test_list_players(self):
        self.lobby.join_lobby("player3", "PYRO:player3@localhost:12345")
        players = self.lobby.list_players()
        self.assertIn("player3", players)
        self.assertEqual("PYRO:player3@localhost:12345", players["player3"])
        self.lobby.leave_lobby("player3")
        players = self.lobby.list_players()
        self.assertNotIn("player3", players)

    def test__is_full(self):
        self.assertTrue(self.lobby.join_lobby("player1", "PYRO:player1@localhost:12345"))
        self.assertTrue(self.lobby.join_lobby("player2", "PYRO:player2@localhost:12345"))
        self.assertTrue(self.lobby.join_lobby("player3", "PYRO:player3@localhost:12345"))
        self.assertFalse(self.lobby.join_lobby("player4", "PYRO:player4@localhost:12345"))
        self.lobby.leave_lobby("player3")
        self.assertTrue(self.lobby.join_lobby("player4", "PYRO:player4@localhost:12345"))
