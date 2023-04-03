"""
Shows the main menu for the game, gets the user name before starting
"""
import sys
from typing import Optional

import pygame
import pygame_widgets
import yaml
from pygame.event import Event

from common.gameconstants import *
from common.logger import log, logger
from common.network import Network
from common.utils import write_file
from gui.button import TextButton, MessageBox, InputText, RadioButton
from gui.gui_common.display import Display
from gui.login.informed_consent import InformedConsent
from gui.login.pregame_survey import PreGameSurvey


class MainMenu:
    BG = (255, 255, 255)

    def __init__(self, user_reset: bool, restore_from_default: bool):
        self.wc_state = WelcomeState.INIT
        self.scr_w, self.scr_h = Display.dims()
        self.x, self.y = self.scr_w // 6, self.scr_h // 6
        self.surface = pygame.Surface.subsurface(Display.surface(),
                                                 (self.x, self.y, self.scr_w // 1.5, self.scr_h // 1.5)
                                                 )

        self.controls: [InputText] = []
        self.user_choices: Optional[RadioButton] = None
        self.cur_input_field = 0

        write_file(CLIENT_DEFAULT_SETTINGS_FILE,
                   lambda _f: yaml.safe_dump(CLIENT_SETTINGS_TEMPLATE, _f))
        write_file(CLIENT_SETTINGS_FILE,
                   lambda _f: yaml.safe_dump(CLIENT_SETTINGS_TEMPLATE, _f))

        if restore_from_default:
            try:
                with open(CLIENT_DEFAULT_SETTINGS_FILE, 'r') as d_fp:
                    write_file(CLIENT_SETTINGS_FILE, lambda _f:
                    yaml.safe_dump(yaml.safe_load(d_fp), _f),
                               overwrite=True)
            except FileNotFoundError as ffe:
                log("INIT ERROR: ", ffe)

        with open(CLIENT_SETTINGS_FILE) as file:
            try:
                self.game_settings = dict(yaml.safe_load(file))
                if user_reset:
                    self.game_settings['user_defaults'] = {}
            except yaml.YAMLError as exc:
                log("settings.yaml error ", exc)
                pygame.quit()
                sys.exit()
        self.login_button: Optional[TextButton] = None
        self.new_user_reg: Optional[TextButton] = None
        self.create_screen_layout()
        self.messagebox = None
        self.svr_defs = self.game_settings['target_server_defaults']
        self.server_ip = self.svr_defs['ip'].strip()
        self.server_port: int = int(self.svr_defs['port'].strip())
        self.server_socket_timeout: int = int(self.svr_defs['socket_timeout'])

        self.informed_consent_done = False

    def on_user_choice(self, o: RadioButton.Option):
        if len(self.controls) > 1:
            self.controls[0].set_text(o.caption)

    def create_screen_layout(self):
        def_usr = ""
        c_x, c_y = self.scr_w // 10, INIT_TILE_SIZE * 1.5
        # if we have exactly one user, its safe to assume it.
        _users = self.game_settings['user_defaults'].keys()
        num_usrs = len(_users)
        if num_usrs == 1:
            def_usr = _users.__iter__().__next__()
        elif num_usrs > 1:
            self.user_choices = RadioButton(21 * TILE_ADJ_MULTIPLIER,
                                            1 * TILE_ADJ_MULTIPLIER,
                                            MAX_NAME_LENGTH + 1,
                                            num_usrs * TILE_ADJ_MULTIPLIER,
                                            on_display=False,
                                            on_option_click=self.on_user_choice,
                                            fill_color=Colors.WHITE)
            for u in _users:
                self.user_choices.add_option(u)
                # def_usr = u if len(def_usr) == 0 else def_usr

        self.controls.append(InputText(self.surface, Display.font(), c_x, c_y,
                                       "Type a Name: ",
                                       def_usr,
                                       in_focus=True))

        button_features = (5 * TILE_ADJ_MULTIPLIER, 1.5 * TILE_ADJ_MULTIPLIER, Colors.GREEN)
        self.login_button = TextButton((self.scr_w // 3.5) // INIT_TILE_SIZE,
                                       (self.scr_h // 2) // INIT_TILE_SIZE,
                                       *button_features, "Login",
                                       visual_effects=True)
        self.new_user_reg = TextButton((self.scr_w // 2.3) // INIT_TILE_SIZE,
                                       (self.scr_h // 2) // INIT_TILE_SIZE,
                                       *button_features, "New User",
                                       visual_effects=True)

    def login(self):
        self.wc_state = WelcomeState.INPUT_COMPLETE

    def draw(self, input_game, events):
        self.surface.fill(Colors.WHITE.value)
        for _c in self.controls:
            _c.draw(self.surface)
        if self.login_button is not None:
            self.login_button.draw(self.surface)

        if self.new_user_reg is not None:
            self.new_user_reg.draw(self.surface)

        if self.user_choices is not None:
            self.user_choices.draw(self.surface)

        if self.messagebox is not None:
            self.messagebox.draw(self.surface)

        pygame_widgets.update(events)  # Call once every loop to allow widgets to render and listen
        pygame.display.update()

        if self.wc_state == WelcomeState.GAME_CONNECT:
            log("done display")

    def run(self, input_game=None):
        run = True
        clock = pygame.time.Clock()
        from gui.gameui import GameUI
        assert input_game is None or isinstance(input_game, GameUI)
        g: GameUI = input_game
        logger.reset()
        while run:
            clock.tick(FPS)
            if self.wc_state == WelcomeState.INPUT_COMPLETE:
                try:
                    if g is None:
                        log("creating GameUI")
                        g = GameUI(self)
                    g.reinitialize()
                    g.handshake()
                    return
                except (OSError, OverflowError) as e:
                    if self.messagebox is None:
                        if isinstance(e, OSError) and e.errno == 61:
                            msg = f"- Server unavailable. Check [{g.ip}:{g.port}] is correct"
                        elif isinstance(e, OSError) and e.errno == 8:
                            msg = f"- Invalid server address. Check [{g.ip}:{g.port}."
                        else:
                            msg = f"- Could not connect to game server {g.ip} - {e}"
                        self.messagebox = MessageBox(self.surface.get_width(), self.surface.get_height(),
                                                     20, 5,
                                                     msg,
                                                     "ok",
                                                     blink=True
                                                     # ,on_ok=lambda: sys.exit(1)
                                                     )
                        self.messagebox.show()
                        self.cur_input_field = 0
                        self.controls[self.cur_input_field].begin_input()
                        if self.user_choices is not None:
                            # self.user_choices.show()
                            pass
                        self.wc_state = WelcomeState.USER_ERR_CONFIRM
                finally:
                    g = input_game

            # %% GameUI delegation end
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    if self.messagebox is not None and \
                            self.messagebox.button_events(event, *mouse):
                        continue

                    ss_mx, ss_my = map(lambda _c: _c[0] - _c[1], zip(mouse, self.surface.get_offset()))

                    def button_mouse_down(button):
                        if button is not None and \
                                button.click(ss_mx, ss_my):
                            button.mouse_down()
                            return True
                        return False

                    if button_mouse_down(self.login_button):
                        continue

                    if button_mouse_down(self.new_user_reg):
                        continue

                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse = pygame.mouse.get_pos()
                    ss_mx, ss_my = map(lambda _c: _c[0] - _c[1], zip(mouse, self.surface.get_offset()))
                    if self.messagebox is not None and \
                            self.messagebox.button_events(event, ss_mx, ss_my):
                        self.messagebox.destroy(self.surface)
                        self.messagebox = None
                        # self.wc_state = WelcomeState.QUIT
                        # run = False
                        # pygame.quit()
                        continue  # modal dialog box.

                    if self.login_button is not None and \
                            self.login_button.click(ss_mx, ss_my):
                        self.login_button.mouse_up()
                        if self.input_validation_failed():
                            continue
                        self.login()
                        continue

                    if self.new_user_reg is not None and \
                            self.new_user_reg.click(ss_mx, ss_my):
                        self.new_user_reg.mouse_up()
                        self.register_new_user()
                        continue

                    if self.user_choices is not None:
                        self.user_choices.click(ss_mx, ss_my)
                        continue

                elif event.type == pygame.QUIT or \
                        (event.type == KEYUP and event.key == K_ESCAPE):
                    run = False
                    pygame.quit()
                    sys.exit()

                elif event.type == VIDEORESIZE:
                    # screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    Display.resize(event, g.refresh_resolution) if g is not None else None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        if self.messagebox is not None:
                            self.messagebox.destroy(self.surface)
                            self.messagebox = None
                            continue

                        if self.input_validation_failed():
                            continue

                        self.move_next_control(event)
                    else:
                        if self.cur_input_field == 0 and \
                                self.user_choices is not None and \
                                self.user_choices.key_up(event):
                            continue

                        mod = event.mod == pygame.KMOD_NONE
                        if mod and (event.key == pygame.K_DOWN or event.key == pygame.K_TAB) \
                                and 0 <= self.cur_input_field < len(self.controls):
                            self.move_next_control(event)
                            continue
                        elif (
                                mod and event.key == pygame.K_UP
                                or
                                (
                                        event.mod & pygame.KMOD_SHIFT and event.key == pygame.K_TAB
                                )
                        ) and 0 <= self.cur_input_field < len(self.controls):
                            self.move_next_control(event, True)

                        # gets the key name
                        key_name = pygame.key.name(event.key)
                        # converts to uppercase the key name
                        key_name = key_name.lower()
                        self.controls[self.cur_input_field].type(key_name)

            # self.surface.fill(Colors.LTS_GRAY.value)
            # self.surface.fill(self.BG)
            self.draw(input_game, events)

        self.save_gamesettings()

    def save_gamesettings(self):
        with open(CLIENT_SETTINGS_FILE, 'w') as fp:
            yaml.safe_dump(self.game_settings, fp)

    def move_next_control(self, event: Event, reverse=False):
        self.controls[self.cur_input_field].end_input()

        if self.cur_input_field == len(self.controls) - 1 and event.key == pygame.K_RETURN:
            self.login()
            return

        if not reverse and self.cur_input_field < len(self.controls) - 1:
            if self.cur_input_field == 0 and self.user_choices is not None:
                self.user_choices.hide()
            self.cur_input_field += 1
        elif reverse and self.cur_input_field > 0:
            self.cur_input_field -= 1
            if self.cur_input_field == 0 and self.user_choices is not None:
                # self.user_choices.show()
                pass
        else:
            return
        self.controls[self.cur_input_field].begin_input()

    def get_ip(self):
        return self.server_ip

    def set_ip(self, ip):
        self.server_ip = ip
        self.svr_defs['ip'] = ip

    def get_port(self):
        return self.server_port

    def set_port(self, port):
        self.server_port = int(port)
        self.svr_defs['port'] = port

    def get_socket_timeout(self):
        return self.server_socket_timeout

    def input_validation_failed(self):
        c = self.controls[self.cur_input_field]
        c.end_input()
        c.hide()
        if len(c.text.strip()) == 0:
            msg = " " + c.p_text + " cannot be empty"
            self.messagebox = MessageBox(self.surface.get_width(), self.surface.get_height(),
                                         20, 5,
                                         msg,
                                         "ok", blink=True)
            self.messagebox.show()
            return True
        return False

    def register_new_user(self):
        try:
            self.controls[self.cur_input_field].hide()
            ic = InformedConsent()
            ic.main()
            self.informed_consent_done = True
            s = PreGameSurvey(self.send_survey)
            s.main()
        finally:
            self.controls[self.cur_input_field].show()

    def send_survey(self, req: ClientMsgReq, msg):
        n = Network(self.get_ip(), self.get_port(), "-", "-", self.get_socket_timeout())
        res = n.send_user_registration(req, msg)
        log(f"Registration {res}")
