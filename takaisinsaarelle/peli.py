import tkinter as tk
import numpy as np
import threading
import time
import random
import simpleaudio

digging_sound = simpleaudio.WaveObject.from_wave_file("digging_sound.wav")

# matriisi
allas = np.zeros((20, 60))
ernestin_oja = np.ones(100)
kernestin_oja = np.ones(100)

root = tk.Tk()
root.title("Autio saari -simulaatio")
canvas = tk.Canvas(root, width=800, height=600)
canvas.pack()

# tarvittavat alueet
canvas.create_rectangle(0, 0, 800, 600, fill='blue')  # meri
canvas.create_oval(100, 100, 700, 500, fill='yellow', outline="")  # saari
canvas.create_rectangle(350, 300, 450, 360, fill='blue')  # uima-allas
ernestin_ojaviiva = canvas.create_line(375, 300, 375, 100, fill='orange', width=5)  # ernestin oja
canvas.create_line(425, 300, 425, 100, fill='orange', width=5)  # kernestin oja
canvas.create_oval(200, 350, 300, 450, fill='green')  # metsä

# selitteet
canvas.create_text(400, 50, text="Autio saari", font=("Arial", 20))
canvas.create_text(250, 400, text="Metsä", fill='black', font=("Arial", 12))
canvas.create_text(400, 380, text="Uima-allas (20x60)", fill='black', font=("Arial", 12))
canvas.create_text(350, 200, text="Ernestin oja (100x1)", fill='black', font=("Arial", 10))
canvas.create_text(450, 200, text="Kernestin oja (100x1)", fill='black', font=("Arial", 10))

apinat = []
# luodaan 10 apinaa
for _ in range(10):
    x = random.randint(200, 300)
    y = random.randint(350, 450)
    apina = canvas.create_oval(x-5, y-5, x+5, y+5, fill='brown')
    apinat.append(apina)

lock = threading.Lock()

def get_monke():
    with lock:
        if apinat:
            return apinat.pop()
    return None

def place_monke(apina):
    x = 375  # Ernestin ojan x-koordinaatti
    y = random.randint(100, 300)
    with lock:
        canvas.coords(apina, x-5, y-5, x+5, y+5)
    return x, y

def dig(apina, x, y):
    digtime = 1
    for i in range(100):  # Muutettu silmukkaa
        time.sleep(digtime)
        with lock:
            if i < len(ernestin_oja):
                ernestin_oja[i] = 0
        root.after(0, update_ui, apina, i)
        digging_sound.play()
        digtime *= 2

def update_ui(apina, i):
    y = 300 - i  # Lasketaan y-koordinaatti
    canvas.coords(apina, 370, y-5, 380, y+5)
    canvas.itemconfig(ernestin_ojaviiva, fill='blue', width=5)

def ernesti_digs():
    apina = get_monke()
    if apina:
        x, y = place_monke(apina)
        t = threading.Thread(target=dig, args=(apina, x, y))
        t.start()

dig_button = tk.Button(root, text="Aloita kaivaminen", command=ernesti_digs)
dig_button.pack()

root.mainloop()
