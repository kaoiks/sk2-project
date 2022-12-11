import dearpygui.dearpygui as dpg
import web_client as wb

WIDTH = 1200
HEIGHT = 700


class SceneManager():

    first_screen = True
    lobby_screen = False
    game_screen = False
    nick_input_id = 0
    web_client = wb.WebClient()

    def __init__(self) -> None:
        dpg.show_viewport()
        self.draw_login_window()

    def __del__(self):
        print("scene_manager deleted")
        self.web_client.close_socket()

    def draw_login_window(self):
        with dpg.window(width=WIDTH, height=HEIGHT, label="login_screen", no_move=True, no_resize=True, no_title_bar=True):
            dpg.add_text("Insert your nickname:",pos=(WIDTH/2 - 150, HEIGHT/2 - 95))
            self.nick_input_id = dpg.add_input_text(tag="nick_input", callback=self.nickname_submitted, width=300, height=150, pos=(WIDTH/2 - 150, HEIGHT/2 - 75), no_spaces=True, multiline=False, on_enter=True)

    def draw_lobby_window(self):
        with dpg.window(width=WIDTH, height=HEIGHT, label="lobby_screen", no_move=True, no_resize=True, no_title_bar=True):
            #dpg.add_text("Insert your nickname:",pos=(WIDTH/2 - 150, HEIGHT/2 - 95))
            self.nick_input_id = dpg.add_input_text(tag="nick_input", callback=self.nickname_submitted, width=300, height=150, pos=(WIDTH/2 - 150, HEIGHT/2 - 75), no_spaces=True, multiline=False, on_enter=True)



    def nickname_submitted(self):
        success = self.web_client.connect_to_server()
        if not success:
            dpg.destroy_context()
        
        self.first_screen = False
        self.lobby_screen = True
        




