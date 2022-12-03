import time
import pygame
import socket

width = 1400
height = 800
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Game Client")

clientNumber = 0


class Player():
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x,y,width,height)
        self.vel = 3

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.vel

        if keys[pygame.K_RIGHT]:
            self.x += self.vel

        if keys[pygame.K_UP]:
            self.y -= self.vel

        if keys[pygame.K_DOWN]:
            self.y += self.vel

        self.rect = (self.x, self.y, self.width, self.height)


def redrawWindow(win,player):
    win.fill((255,255,255))
    player.draw(win)
    pygame.display.update()


def main():
    run = True
    p = Player(50,50,100,100,(0,255,0))
    clock = pygame.time.Clock()
    server = ("127.0.0.1",8080)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server)
    time.sleep(1)
    data = client_socket.recv(1024)
    print(data)
    client_socket.close()


    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                client_socket.close()
                pygame.quit()

        p.move()
        redrawWindow(win, p)

main()