import tkinter as tk
import numpy as np
import threading
import time
import random
import pygame

pygame.init()
pygame.mixer.init()

digging_sound = pygame.mixer.Sound("digging_sound.wav")

# matriisi
allas = np.zeros((20, 60))
ernestin_oja = np.ones((100, 1))
kernestin_oja = np.ones((100, 1))

root = tk.Tk()
root.title("Autio saari -simulaatio")
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack()

# tarvittavat alueet

# meri
canvas.create_rectangle(0, 0, 800, 600, fill='blue')

# saari
canvas.create_oval(100, 100, 700, 500, fill='yellow', outline="")

# uima-allas
canvas.create_rectangle(350, 300, 450, 360, fill='blue')  # Muutettu korkeutta vastaamaan 20x60 suhdetta

# ernestin oja
canvas.create_line(375, 300, 375, 100, fill='orange', width=5)  # Muutettu kulkemaan ylös

# kernestin oja
canvas.create_line(425, 300, 425, 100, fill='orange', width=5)  # Muutettu kulkemaan ylös

# metsä
canvas.create_oval(200, 350, 300, 450, fill='green')  # Siirretty etelään

# selitteet
canvas.create_text(400, 50, text="Autio saari", font=("Arial", 20))
canvas.create_text(250, 400, text="Metsä", fill='black', font=("Arial", 12))  # Päivitetty sijainti
canvas.create_text(400, 380, text="Uima-allas (20x60)", fill='black', font=("Arial", 12))
canvas.create_text(350, 200, text="Ernestin oja (100x1)", fill='black', font=("Arial", 10))  # Päivitetty sijainti
canvas.create_text(450, 200, text="Kernestin oja (100x1)", fill='black', font=("Arial", 10))  # Päivitetty sijainti

apinat = []
# luodaan 10 apinaa
for _ in range(10):
    x = random.randint(300, 500)
    y = random.randint(350, 450)
    apina = canvas.create_oval(x-5, y-5, x+5, y+5, fill='brown')
    apinat.append(apina)

def get_monke():
    if apinat:
        return apinat.pop()
    return None

def place_monke(apina):
    x = random.randint(375, 425)
    y = random.randint(100, 300)
    canvas.coords(apina, x-5, y-5, x+5, y+5)
    return x, y

def dig(apina, x, y):
    digtime = 1
    for i in range(y, 100, -1):
        time.sleep(digtime)
        canvas.move(apina, 0, -1)
        ernestin_oja[i-100] = 0
        canvas.itemconfig(ernestin_ojaviiva, fill='blue')
        digging_sound.play()
        root.update()
        digtime *= 2

def ernesti_digs():
    apina = get_monke()
    if apina:
        x, y = place_monke(apina)
        t = threading.Thread(target=dig, args=(apina, x, y))
        t.start()

ernestin_ojaviiva = canvas.create_line(375, 300, 375, 100, fill='orange', width=5)

dig_button = tk.Button(root, text="aloita kaivaminen", command=ernesti_digs)

root.mainloop()
