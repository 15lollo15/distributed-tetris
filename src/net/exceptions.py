import Pyro4.util


class PlayerAlreadyIn(Exception):
    pass


class LobbyFull(Exception):
    pass


class PlayerNotInLobby(Exception):
    pass


Pyro4.util.SerializerBase.register_dict_to_class("net.exceptions.PlayerAlreadyIn", PlayerAlreadyIn)
Pyro4.util.SerializerBase.register_dict_to_class("net.exceptions.LobbyFull", LobbyFull)
Pyro4.util.SerializerBase.register_dict_to_class("net.exceptions.PlayerNotInLobby", PlayerNotInLobby)
