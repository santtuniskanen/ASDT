import tkinter as tk
from tkinter import PhotoImage, messagebox
import random
import pygame
from collections import Counter

class Monkey:
    def __init__(self, canvas, start_y, sender, word, image):
        self.canvas = canvas
        self.image = image
        self.id = canvas.create_image(150, start_y, image=self.image, anchor=tk.NW)
        self.sender = sender
        self.word = word
        self.distance = 0
        self.last_sound_distance = 0
        self.total_distance = 1000

    def move(self):
        move_distance = self.total_distance / 100
        self.canvas.move(self.id, move_distance, 0)
        self.distance += move_distance
        if int(self.distance / (self.total_distance / 10)) > int(self.last_sound_distance / (self.total_distance / 10)):
            pygame.mixer.Sound("swim.wav").play()
            self.last_sound_distance = self.distance

        if self.distance >= self.total_distance:
            self.canvas.delete(self.id)
            pygame.mixer.Sound("arrival.wav").play()
            return False

        return True

class Shark:
    def __init__(self, canvas, image):
        self.canvas = canvas
        self.image = image
        self.id = canvas.create_image(random.randint(200, 1000), random.randint(100, 600), image=self.image, anchor=tk.NW)
        self.speed_x = random.choice([-2, -1, 1, 2])
        self.speed_y = random.choice([-2, -1, 1, 2])

    def move(self):
        self.canvas.move(self.id, self.speed_x, self.speed_y)
        x, y = self.canvas.coords(self.id)
        if x <= 200 or x >= 1000:
            self.speed_x *= -1
        if y <= 100 or y >= 600:
            self.speed_y *= -1

class HarbourGuard:
    def __init__(self, name, y, original_message):
        self.name = name
        self.y = y
        self.original_message = original_message.split()
        self.words = []

    def check_monkey(self, word):
        if word not in self.words:
            self.words.append(word)
        return len(self.words) >= 16

    def get_message(self):
        ordered_words = [word for word in self.original_message if word in self.words]
        return " ".join(ordered_words)

class Game:
    def __init__(self, master):
        self.master = master
        self.master.title("Ernesti ja Kernesti autiolla saarella")
        self.master.geometry("1920x900")

        self.canvas = tk.Canvas(self.master, width=1920, height=700, bg="white")
        self.canvas.pack()

        pygame.mixer.init()

        self.saari = PhotoImage(file='saari.png')
        self.mantere = PhotoImage(file='mantere.png')
        self.monkey_image = PhotoImage(file='monke.png')
        self.ship_image = PhotoImage(file='ship.png')
        self.shark_image = PhotoImage(file='shark.png')

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.saari)
        self.canvas.create_image(1000, 0, anchor=tk.NW, image=self.mantere)

        self.ernesti_frame = tk.Frame(self.master)
        self.ernesti_frame.pack(side=tk.LEFT, padx=10)

        self.kernesti_frame = tk.Frame(self.master)
        self.kernesti_frame.pack(side=tk.RIGHT, padx=10)

        self.ernesti_button = tk.Button(self.ernesti_frame, text="Ernesti: Lähetä apina", command=lambda: self.send_monkey("Ernesti"))
        self.ernesti_button.pack(pady=5)

        self.ernesti_group_button = tk.Button(self.ernesti_frame, text="Ernesti: Lähetä 10 apinaa", command=lambda: self.send_monkey_group("Ernesti"))
        self.ernesti_group_button.pack(pady=5)

        self.kernesti_button = tk.Button(self.kernesti_frame, text="Kernesti: Lähetä apina", command=lambda: self.send_monkey("Kernesti"))
        self.kernesti_button.pack(pady=5)

        self.kernesti_group_button = tk.Button(self.kernesti_frame, text="Kernesti: Lähetä 10 apinaa", command=lambda: self.send_monkey_group("Kernesti"))
        self.kernesti_group_button.pack(pady=5)

        self.message = "Ernesti ja Kernesti tässä terve! Olemme autiolla saarella, voisiko joku tulla sieltä sivistyneestä maailmasta hakemaan meidät pois! Kiitos!"
        self.words = self.message.split()

        self.ernesti_monkeys = 0
        self.kernesti_monkeys = 0

        self.monkeys = []
        self.sharks = [Shark(self.canvas, self.shark_image) for _ in range(10)]
        self.animation_id = None

        self.pohteri = HarbourGuard("Pohteri", 100, self.message)
        self.eteteri = HarbourGuard("Eteteri", 700, self.message)

        self.pohteri_label = tk.Label(self.ernesti_frame, text=f"{self.pohteri.name}: 0 sanaa")
        self.pohteri_label.pack(pady=5)
        self.pohteri_button = tk.Button(self.ernesti_frame, text="Näytä Pohterin viesti", command=lambda: self.show_guard_message(self.pohteri))
        self.pohteri_button.pack(pady=5)

        self.eteteri_label = tk.Label(self.kernesti_frame, text=f"{self.eteteri.name}: 0 sanaa")
        self.eteteri_label.pack(pady=5)
        self.eteteri_button = tk.Button(self.kernesti_frame, text="Näytä Eteterin viesti", command=lambda: self.show_guard_message(self.eteteri))
        self.eteteri_button.pack(pady=5)

        self.rescue_initiated = False

    def send_monkey(self, sender):
        start_y = 280 if sender == "Ernesti" else 580  # Adjusted Y positions
        word = random.choice(self.words)
        monkey = Monkey(self.canvas, start_y, sender, word, self.monkey_image)
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
                # Check for collision with sharks
                monkey_bbox = self.canvas.bbox(monkey.id)
                for shark in self.sharks:
                    shark_bbox = self.canvas.bbox(shark.id)
                    if self.check_collision(monkey_bbox, shark_bbox):
                        self.canvas.delete(monkey.id)
                        self.monkeys.remove(monkey)
                        pygame.mixer.Sound("shark_attack.wav").play()
                        break
            else:
                self.monkeys.remove(monkey)
                if monkey.distance >= monkey.total_distance:  # Monkey reached the mainland
                    if monkey.sender == "Ernesti":
                        self.ernesti_monkeys += 1
                        if self.pohteri.check_monkey(monkey.word) and not self.rescue_initiated:
                            self.rescue("Ernesti")
                    else:
                        self.kernesti_monkeys += 1
                        if self.eteteri.check_monkey(monkey.word) and not self.rescue_initiated:
                            self.rescue("Kernesti")
                    self.update_guard_labels()

        for shark in self.sharks:
            shark.move()

        if still_moving:
            self.animation_id = self.master.after(50, self.animate)
        else:
            self.animation_id = None

    def check_collision(self, bbox1, bbox2):
        return not (bbox1[2] < bbox2[0] or bbox1[0] > bbox2[2] or bbox1[3] < bbox2[1] or bbox1[1] > bbox2[3])

    def update_guard_labels(self):
        self.pohteri_label.config(text=f"{self.pohteri.name}: {len(self.pohteri.words)} sanaa")
        self.eteteri_label.config(text=f"{self.eteteri.name}: {len(self.eteteri.words)} sanaa")

    def show_guard_message(self, guard):
        messagebox.showinfo(f"{guard.name}n viesti", guard.get_message())

    def rescue(self, winner):
        if self.rescue_initiated:
            return

        self.rescue_initiated = True
        rescue_ship = self.canvas.create_image(1000, 400, image=self.ship_image, anchor=tk.NW)

        def move_ship():
            nonlocal rescue_ship
            if self.canvas.coords(rescue_ship)[0] > 150:
                self.canvas.move(rescue_ship, -10, 0)
                self.master.after(50, move_ship)
            else:
                pygame.mixer.Sound("victory.wav").play()
                messagebox.showinfo("Pelastus!", f"{winner} sai ensimmäisenä viestin perille! Pelastuslaiva on saapunut!")
                self.calculate_feast()
                self.end_game()

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

    def end_game(self):
        # Stop all animations
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
            self.animation_id = None

        for monkey in self.monkeys:
            self.canvas.delete(monkey.id)
        self.monkeys.clear()

        for shark in self.sharks:
            self.canvas.delete(shark.id)
        self.sharks.clear()

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
