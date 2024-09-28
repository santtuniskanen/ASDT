import tkinter as tk
from tkinter import PhotoImage, messagebox
import random
import pygame
from collections import Counter

pygame.mixer.init()

# Ladataan ä
saari = PhotoImage(file='saari.png')
mantere = PhotoImage(file='mantere.jpg')
swim_sound = pygame.mixer.Sound("swim.wav")
shark_attack_sound = pygame.mixer.Sound("shark_attack.wav")
arrival_sound = pygame.mixer.Sound("arrival.wav")
victory_sound = pygame.mixer.Sound("victory.wav")

class Monkey:
    def __init__(self, canvas, start_y, sender, word):
        self.canvas = canvas
        self.id = canvas.create_oval(100, start_y, 110, start_y + 10, fill="brown")
        self.sender = sender
        self.word = word
        self.distance = 0
        self.last_sound_distance = 0

    def move(self):
        if random.random() < 0.01:  # 1% todennäköisyys tulla syödyksi
            self.canvas.delete(self.id)
            shark_attack_sound.play()
            return False

        self.canvas.move(self.id, 6, 0)
        self.distance += 1
        if self.distance - self.last_sound_distance >= 10:
            swim_sound.play()
            self.last_sound_distance = self.distance

        if self.distance >= 100:
            self.canvas.delete(self.id)
            arrival_sound.play()
            return False

        return True

class Game:
    def __init__(self, master):
        self.master = master
        self.master.title("Ernesti ja Kernesti autiolla saarella")
        self.canvas = tk.Canvas(self.master, width=1600, height=600, bg="white")
        self.canvas.pack()

        # Piirrä saari ja manner
        self.canvas.create_image(saari)
        self.canvas.create_image(mantere)

        # Napit apinoille
        self.ernesti_button = tk.Button(self.master, text="Ernesti: Lähetä apina", command=lambda: self.send_monkey("Ernesti"))
        self.ernesti_button.pack()
        self.kernesti_button = tk.Button(self.master, text="Kernesti: Lähetä apina", command=lambda: self.send_monkey("Kernesti"))
        self.kernesti_button.pack()

        # Napit kymmenelle apinalle
        self.ernesti_group_button = tk.Button(self.master, text="Ernesti: Lähetä 10 apinaa", command=lambda: self.send_monkey_group("Ernesti"))
        self.ernesti_group_button.pack()
        self.kernesti_group_button = tk.Button(self.master, text="Kernesti: Lähetä 10 apinaa", command=lambda: self.send_monkey_group("Kernesti"))
        self.kernesti_group_button.pack()

        self.message = "Ernesti ja Kernesti tässä terve! Olemme autiolla saarella, voisiko joku tulla sieltä sivistyneestä maailmasta hakemaan meidät pois! Kiitos!"
        self.words = self.message.split()

        self.ernesti_words = set()
        self.kernesti_words = set()
        self.ernesti_monkeys = 0
        self.kernesti_monkeys = 0

        self.monkeys = []
        self.animation_id = None

    def draw_island(self, x, y, width, height):
        self.canvas.create_image(saari)

    def draw_mainland(self, x, y, width, height):
        self.canvas.create_image(mantere)

    def send_monkey(self, sender):
        start_y = 220 if sender == "Ernesti" else 280
        word = random.choice(self.words)
        monkey = Monkey(self.canvas, start_y, sender, word)
        self.monkeys.append(monkey)

        if self.animation_id is None:
            self.animate()

    def send_monkey_group(self, sender):
        for _ in range(10):
            self.send_monkey(sender)

    def animate(self):
        still_moving = False
        for monkey in self.monkeys[:]:
            if monkey.move():
                still_moving = True
            else:
                self.monkeys.remove(monkey)
                if monkey.distance >= 100:  # Apina pääsi perille
                    if monkey.sender == "Ernesti":
                        self.ernesti_words.add(monkey.word)
                        self.ernesti_monkeys += 1
                    else:
                        self.kernesti_words.add(monkey.word)
                        self.kernesti_monkeys += 1
                    self.check_rescue()

        if still_moving:
            self.animation_id = self.master.after(50, self.animate)
        else:
            self.animation_id = None

    def check_rescue(self):
        if len(self.ernesti_words) > 10:
            self.rescue("Ernesti")
        elif len(self.kernesti_words) > 10:
            self.rescue("Kernesti")

    def rescue(self, winner):
        rescue_ship = self.canvas.create_rectangle(700, 200, 750, 250, fill="blue")

        def move_ship():
            nonlocal rescue_ship
            if self.canvas.coords(rescue_ship)[0] > 100:
                self.canvas.move(rescue_ship, -6, 0)
                self.master.after(50, move_ship)
            else:
                messagebox.showinfo("Pelastus!", f"{winner} sai ensimmäisenä viestin perille! Pelastuslaiva on saapunut!")
                self.calculate_feast()

        move_ship()

    def calculate_feast(self):
        ernesti_guests = self.ernesti_monkeys * 4
        kernesti_guests = self.kernesti_monkeys * 4

        ernesti_pepper = (self.ernesti_monkeys * 2)
        kernesti_pepper = (self.kernesti_monkeys * 2)

        total_pepper = ernesti_pepper + kernesti_pepper

        feast_info = f"""
        Ernestin juhlissa: {ernesti_guests} vierasta
        Kernestin juhlissa: {kernesti_guests} vierasta

        Mustapippuria käytettiin yhteensä: {total_pepper} teelusikkaa

        {'Ernestillä' if ernesti_guests > kernesti_guests else 'Kernestillä'} oli isommat juhlat!
        """

        messagebox.showinfo("Juhlat", feast_info)

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
