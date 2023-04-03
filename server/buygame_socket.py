from _socket import SHUT_RDWR
from datetime import datetime

from common.logger import log
from common.player import Player


class ClientSocket:
    def __init__(self, c_soc, client_address):
        from socket import socket
        self.socket: socket = c_soc
        self.c_addr = client_address
        self.last_hb_received = datetime.now()
        self.is_active = True
        self.player = None
        self.thread_name: str = ""
        self.closed = False

    def __repr__(self):
        return f"{self.player.game.game_id}-{self.player.name}-{self.player.number}"

    def post_handshake(self, g_id: int, player: Player):
        assert player.game.game_id == g_id
        self.player = player
        self.thread_name = f"{self.player.name}-{self.player.number}-{self.player.game.game_id}"

    def set_last_active_ts(self):
        self.last_hb_received = datetime.now()

    def mark_inactive(self):
        self.is_active = False

    def close(self, threads_list):
        if self.closed:
            return
        log(f"closing client {self.player.number} connection.")
        # connection closed
        try:
            self.socket.shutdown(SHUT_RDWR)
            self.socket.close()
        except OSError as ignore:
            # skip 57 - Socket is not connected
            if not ignore.errno == 57:
                log(f"ignoring unexpected OSError", ignore)
        finally:
            for i in range(len(threads_list)):
                if threads_list[i].name == self.thread_name:
                    threads_list.pop(i)
                    log(f"cleaned up {self.thread_name} thread.")
                    self.closed = True
                    break
