import dearpygui.dearpygui as dpg
import scene_manager as sm

dpg.create_context()
dpg.create_viewport(title='Hangman The Game', width=1200, height=700, resizable=False)
dpg.setup_dearpygui()

def main():
    try:
        scene_manager = sm.SceneManager()
        
        last_screen = "LOGIN"
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()

            if last_screen == "LOGIN" and scene_manager.lobby_screen == True:
                last_screen = "LOBBY"
                dpg.delete_item(dpg.get_active_window())
                scene_manager.draw_lobby_window()
            
        scene_manager.web_client.close_socket()
    except Exception as e:
        print(e)
        scene_manager.web_client.close_socket()
main()