import PySimpleGUI as sg
import threading
import time
import socket
import json
import logging
import math

logging.basicConfig(level=logging.DEBUG)
sg.theme('Dark')

class Game:
    def __init__(self):
        self.initialize_socket()
        self.listen_for_incoming_messages_in_a_thread()
        self.nickname_frame = None
        self.accepted_nickname = False
        self.window = None
        self.current_round = 0
        self.current_word = ""
        self.game_in_progress = False
        self.guessed_letters = []
        self.bad_guesses = []
        self.lifes = 9
        self.nickname = None
    def initialize_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        remote_ip = '127.0.0.1' 
        remote_port = 8888 
        self.client_socket.connect((remote_ip, remote_port)) 

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def draw_current_canvas(self):
        x = 350 - math.ceil(len(self.current_word)/2) * 25
        y = 550 
        self.window['canvas'].TKCanvas.delete("all")

        if self.lifes < 9:
            self.window['canvas'].TKCanvas.create_line(350, 450, 550, 450, fill='white')
            self.window['canvas'].TKCanvas.create_line(450, 450, 450, 150, fill='white')
        if self.lifes < 8:
            self.window['canvas'].TKCanvas.create_line(450, 150, 350, 150, fill='white')
        if self.lifes < 7:
            self.window['canvas'].TKCanvas.create_line(350, 150, 350, 200, fill='white')
        if self.lifes < 6:
            self.window['canvas'].TKCanvas.create_oval(325, 200, 375, 250, fill='white')
        if self.lifes < 5:
            self.window['canvas'].TKCanvas.create_line(350, 250, 330, 300, fill='white')
        if self.lifes < 4:
            self.window['canvas'].TKCanvas.create_line(350, 250, 370, 300, fill='white')
        if self.lifes < 3:
            self.window['canvas'].TKCanvas.create_line(350, 200, 350, 325, fill='white')
        if self.lifes < 2:
            self.window['canvas'].TKCanvas.create_line(350, 325, 330, 375, fill='white')
        if self.lifes < 1:
            self.window['canvas'].TKCanvas.create_line(350, 325, 370, 375, fill='white')
        



        for letter in self.current_word:
            if letter == " ":
                self.window['canvas'].TKCanvas.create_text(x, y, text=" ", font=("Arial", 20),fill='white')
            else:
                if letter in self.guessed_letters or self.lifes < 1:
                    self.window['canvas'].TKCanvas.create_text(x, y, text=letter, font=("Arial", 20),fill='white')
                else:
                    self.window['canvas'].TKCanvas.create_text(x, y, text="_", font=("Arial", 20),fill='white')
            x += 25

    def receive_message_from_server(self, so):
        while True:
            try:
                buffer = so.recv(4096)
                if not buffer:
                    break

                message = buffer.decode('utf-8')
                print(message)
                data = json.loads(message)

                if 'response' in data:
                    if data['response'] == 1:
                        print("ACCEPTED")
                        self.window['login_button'].update(disabled=True)
                        self.window['nickname_input'].update(disabled=True)  
                        self.accepted_nickname = True
                    else:
                        print("NOT ACCEPTED")
                        self.accepted_nickname = False  
                
                if 'message' in data:
                    if data['message'] == 'IN_LOBBY':
                        self.game_in_progress = False
                        self.window['ranking_text'].Update("")
                        self.window['canvas'].TKCanvas.delete("all")
                        self.window['game_status'].Update("WAITING FOR PLAYERS")
                    if data['message'] == "10_SECOND_ALERT":
                        self.window['game_status'].Update("GAME WILL START IN 10 SECONDS")
                    if data['message'] == "IN_GAME":
                        self.window['game_status'].Update("GAME IN PROGRESS")
                    if data['message'] == 'GAME_STATUS':
                        self.current_round = data['round']
                        self.current_word = data['word']
                        self.game_in_progress = True
                        self.guessed_letters.clear()
                        self.guessed_letters.append(' ')
                        self.bad_guesses.clear()
                        self.lifes = 9
                        ranking  = data['ranking']
                        print(ranking)
                        sorted_ranking = dict(sorted(ranking.items(), key=lambda item: item[1]))
                        self.window['ranking_text'].Update("")

                        ranking_string = ""

                        for key in reversed(list(sorted_ranking.keys())):
                            ranking_string += f"{key} - {sorted_ranking[key]}\n"
                        self.window['ranking_text'].Update(ranking_string)
                        x = 350 - math.ceil(len(self.current_word)/2) * 25
                        y = 550 
                        self.draw_current_canvas()
                    if data['message'] == 'SHOW_RANKING':
                        self.ra
                        self.game_in_progress = False
                        self.guessed_letters.clear()
                        self.guessed_letters.append(' ')
                        self.bad_guesses.clear()
                        self.lifes = 9
                        x = 350 - math.ceil(len(self.current_word)/2) * 25
                        y = 550 
                        self.draw_current_canvas()    

            except ConnectionAbortedError:
                break
        
        so.close()
        self.window.Close()
        exit(0)

    def submit_nickname(self, nickname):
        for _ in range(5):
            try:
                message = {
                    'operation': 'SET_NAME',
                    'username': nickname
                }
                print((json.dumps(message) + "\n").encode('utf-8'))
                self.client_socket.sendall((json.dumps(message) + "\n").encode('utf-8'))
                break
                
            except Exception:
                print("TIMEOUT")
                time.sleep(1)
                continue
        return False



    def send_guessed_info(self):
        message = {
                    'operation': 'GUESSED',
                    'username': self.nickname,
                    'round': self.current_round
                }
        print(message)
        print((json.dumps(message) + "\n").encode('utf-8'))
        self.client_socket.sendall((json.dumps(message) + "\n").encode('utf-8'))
    
    def send_not_guessed_info(self):
        message = {
                    'operation': 'NOT_GUESSED',
                    'username': self.nickname,
                    'round': self.current_round
                }
        print((json.dumps(message) + "\n").encode('utf-8'))
        self.client_socket.sendall((json.dumps(message) + "\n").encode('utf-8'))

    def check_if_win(self):
        for letter in self.current_word:
            if not letter in self.guessed_letters:
                return False
        return True
    def hangman_game(self):
        layout_guess = [
                    [sg.Text('Letter:', size=(15,1)), sg.InputText(enable_events=True, key='letter_input')],
                    [sg.Button('Guess', key='make_guess')] ]

        login_layout = [
                    [sg.Text('Choose your nickname:')],
                    [sg.InputText( key='nickname_input')],
                    [sg.Button('Submit', key='login_button')]
                ]
        
        
        col2 = sg.Column([[sg.Canvas(size=(700, 700), background_color='black', key='canvas')]],pad=(0,0))
        col3 = sg.Column([
                        [sg.Frame('Set Nickname', login_layout, key='login_frame')],
                        [sg.Frame(['Guessing'], layout_guess)],
                        [sg.Text('WAITING FOR PLAYERS', key='game_status')],
                        
                        [sg.Text('GAME RANKING:', key='ranking_label', font=("Arial", 20))],
                        [sg.Text('', key='ranking_text', font=("Arial", 20))]
                        ], pad=(0,0)) 
        layout = [
            sg.vtop([col3, col2])
        ]

        
        window = sg.Window('Hangman Game', layout, element_justification='c', size=(1200, 700), finalize=True)
        self.window = window

        

        while True:
            event, values = window.Read()
            logging.debug(event)
            if event == "letter_input":
                if len(values['letter_input']) > 1:
                    window.Element('letter_input').Update(values['letter_input'][:-1])
                elif len(values['letter_input']) == 1:
                    if values['letter_input'].isalpha():
                        window.Element('letter_input').Update(values['letter_input'].upper())
                    else:
                        window.Element('letter_input').Update('')
            if event == 'login_button' and not self.accepted_nickname:
                if len(values['nickname_input']) == 0:
                    continue
                self.nickname = values['nickname_input']
                self.submit_nickname(values['nickname_input'])
            
            if event == 'make_guess' and self.game_in_progress and self.lifes > 0 and not self.check_if_win():
                letter = values['letter_input']
                window.Element('letter_input').Update("")
                self.window['letter_input'].set_focus()
                if letter in self.bad_guesses:
                    continue
                elif letter in self.guessed_letters:
                    continue
                elif letter in self.current_word:
                    self.guessed_letters.append(letter)
                    self.draw_current_canvas()
                    print(self.check_if_win())
                    if self.check_if_win():
                        self.send_guessed_info()

                else:
                    self.bad_guesses.append(letter)
                    self.lifes -= 1
                    if self.lifes == 0:
                        self.send_not_guessed_info()
                    self.draw_current_canvas()
            

            if event == sg.WIN_CLOSED:
                break
        window.Close()
        self.client_socket.close()
        exit(0)

Game().hangman_game()