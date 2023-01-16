import dearpygui.dearpygui as dpg
import scene_manager as sm
import time
import threading


dpg.create_context()
dpg.create_viewport(title='Hangman The Game', width=1200, height=700, resizable=False)
dpg.setup_dearpygui()
dpg.set_global_font_scale(1.1)

def main():
    try:
        scene_manager = sm.SceneManager()
        
        last_screen = "LOGIN"
        while dpg.is_dearpygui_running():
            time.sleep(0.01)
            dpg.render_dearpygui_frame()

            if last_screen == "LOGIN" and scene_manager.lobby_screen:
                last_screen = "LOBBY"
                dpg.delete_item(dpg.get_active_window())
                scene_manager.draw_lobby_window()
            # if last_screen == "LOBBY" and scene_manager.lobby_screen:
            #     starting = scene_manager.web_client.get_lobby_status()
            #     if starting:
            #         print("GAME IS STARTING")
            #     else:
            #         print("WAITING FOR PLAYERS")
            #         time.sleep(1)
        scene_manager.web_client.close_socket()
    except Exception as e:
        print(e)
        scene_manager.web_client.close_socket()
        
main()
