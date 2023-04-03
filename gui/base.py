import pygame
import sys

from common.logger import log
from gui.gui_common.display import Display
from gui.main_menu import MainMenu
from common.gameconstants import *


class SpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error:
            log("Unable to load: %s " % filename)
            raise SystemExit

    def crop_out_sprites(self, width: int = 128, height: int = 128):
        all_sprites = [[pygame.Surface([width, height]) for _ in range(5)] for _ in range(6)]
        for j in range(0, 6):
            for i in range(0, 5):
                surf = all_sprites[j][i]
                surf.blit(self.sheet, (0, 0), (i * width, j * height, width, height))
                pygame.draw.rect(surf, Colors.BLACK.value, (0, 0, width - 1, height - 1), 1)
        if VERBOSE:
            for x in all_sprites:
                for y in x:
                    print(y.get_size())
        return all_sprites


def main():
    _reset = _restore = False
    user = server = ""
    port = 0
    import re

    for i in range(len(sys.argv)):
        if re.match("-ur|--user-reset", sys.argv[i].lower().strip()):
            _reset = True
        elif re.match("-rs|--restore", sys.argv[i].lower().strip()):
            _restore = True
        elif re.match("-u[\b]*|--user=", sys.argv[i].lower().strip()):
            if sys.argv[i].strip() == "-u":
                i += 1 if i < len(sys.argv) - 1 else 0
                user = sys.argv[i]
            else:
                user = str(sys.argv[i]).split('=')[1]

        elif re.match("-s[\b]*|--server=", sys.argv[i].lower().strip()):
            if sys.argv[i].strip() == "-s":
                i += 1 if i < len(sys.argv) - 1 else 0
                server = sys.argv[i]
            else:
                server = str(sys.argv[i]).split('=')[1]
        elif re.match("-p[\b]*|--port=", sys.argv[i].lower().strip()):
            if sys.argv[i].strip() == "-p":
                i += 1 if i < len(sys.argv) - 1 else 0
                port = int(sys.argv[i])
            else:
                port = int(sys.argv[i].split('=')[1])

    Display.init()

    _main_m = MainMenu(_reset, _restore)

    if len(server.strip()) > 0:
        _main_m.set_ip(server.strip())

    if port > 0:
        _main_m.set_port(port)

    _main_m.controls[0].set_text(user if len(user) > 0 else None)
    from gui.gameui import GameUI
    gui = GameUI(_main_m)
    gui.main()


if __name__ == "__main__":
    main()
