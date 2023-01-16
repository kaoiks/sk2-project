import dearpygui.dearpygui as dpg
import web_client as wb

WIDTH = 1200
HEIGHT = 700


class SceneManager():

    first_screen = True
    lobby_screen = False
    game_screen = False
    nick_input = 0
    web_client = wb.WebClient()
    nick_warning = 0
    submit_button = 0

    def __init__(self) -> None:
        dpg.show_viewport()
        self.draw_login_window(False)

    def __del__(self):
        print("scene_manager deleted")
        self.web_client.close_socket()

    def draw_login_window(self, show_warning):
        with dpg.window(width=WIDTH, height=HEIGHT, label="login_screen", no_move=True, no_resize=True, no_title_bar=True):
            dpg.add_text("Insert your nickname:", pos=(WIDTH/2 - 150, HEIGHT/2 - 95))
            self.nick_input = dpg.add_input_text(tag="nick_input", callback=self.nickname_submitted,
             width=300, height=150, pos=(WIDTH/2 - 150, HEIGHT/2 - 75), no_spaces=True, multiline=False, on_enter=True)
            self.submit_button = dpg.add_button(label="SUBMIT", tag="submit_button", callback=self.nickname_submitted,
             width=80, height=20, pos=(WIDTH/2 + 170, HEIGHT/2 - 75)) 
            self.nick_warning = dpg.add_text("Choose another nickname", tag="nick_warning",pos=(WIDTH/2 - 150, HEIGHT/2 - 50), show=show_warning, color=(255,0,0))
            
    def draw_lobby_window(self):
        with dpg.window(width=WIDTH, height=HEIGHT, label="lobby_screen", no_move=True, no_resize=True, no_title_bar=True):
            dpg.add_text("WAITING FOR PLAYERS", pos=(WIDTH/2 - 75, HEIGHT/2 - 50))
    
    def draw_game_window(self):
        with dpg.window(width=WIDTH, height=HEIGHT, label="game_screen", no_move=True, no_resize=True, no_title_bar=True):
            dpg.add_text("Insert your nickname:", pos=(WIDTH/2 - 150, HEIGHT/2 - 95))
            
            

    # Checking if nickname is available
    def nickname_submitted(self, sender):
        print("TRYING TO ADD NICKNAME")
        success = self.web_client.connect_to_server(dpg.get_value(self.nick_input))
        if not success:
            dpg.show_item("nick_warning")
            
        else:
            self.first_screen = False
            self.lobby_screen = True
        
    