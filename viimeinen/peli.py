"""
Apinapeli Mk3 - Santtu Niskanen
"""
from typing import Any, List, Dict, Tuple
import tkinter as tk
import winsound
import random
import time
import threading
import math

class Saarisimulaattori:
    def __init__(self, master: tk.Tk) -> None:
        self.master: tk.Tk = master
        self.master.title("Saarisimulaattori")

        self.canvas: tk.Canvas = tk.Canvas(self.master, width=800, height=600, bg='blue')
        self.canvas.pack()
        
        self.max_saaret: int = 10
        self.saaret: List[Tuple[int, int, int]] = []
        self.apinat: List[Dict[str, Any]] = []
        self.uivat_apinat: List[Dict[str, Any]] = []
        self.saari_koko: int = 50

        self.tulivuori_nappi: tk.Button = tk.Button(self.master, text="Tulivuorenpurkaus", command=self.tee_saari)
        self.tulivuori_nappi.pack()

        self.tyhjenna_nappi: tk.Button = tk.Button(self.master, text="Tyhjennä meri", command=self.tyhjenna_meri)
        self.tyhjenna_nappi.pack()

        self.tee_10_saarta_nappi: tk.Button = tk.Button(self.master, text="Lisää 10 saarta", command=self.tee_10_saarta)
        self.tee_10_saarta_nappi.pack()

        self.uimaan_nappi: tk.Button = tk.Button(self.master, text="Lähetä apina uimaan", command=self.laheta_apina_uimaan)
        self.uimaan_nappi.pack()

        self.apina_maara_var = tk.StringVar()
        self.apina_maara_label = tk.Label(self.master, textvariable=self.apina_maara_var)
        self.apina_maara_label.pack()
        self.paivita_apina_maara()

        threading.Thread(target=self.apinan_aanet, daemon=True).start()
        threading.Thread(target=self.apinoiden_elama, daemon=True).start()
        threading.Thread(target=self.uivien_apinoiden_elama, daemon=True).start()

    def tee_saari(self, soita_aani: bool = True) -> None:
        """Funktio tarkistaa ensin onko 'saaret' listassa jo tarpeeksi monta saarta. 
        Tämän jälkeen funktio menee looppiin, jossa se luo satunnaisesti x ja y arvot 
        ja tarkistaa leikkaako saari toisen saaren. 
        Tämän jälkeen jatketaan saaren luomiseen ja lisätään se 'saaret' listaan."""
        if len(self.saaret) >= self.max_saaret:
            print("Meri on täynnä saaria!")
            return

        while True:
            x: int = random.randint(0, 800 - self.saari_koko)
            y: int = random.randint(0, 600 - self.saari_koko)

            if not any(self.saaret_leikkaa(x, y, saari) for saari in self.saaret):
                saari: int = self.canvas.create_oval(x, y, x + self.saari_koko, y + self.saari_koko, fill='green')
                self.saaret.append((x, y, saari))
                self.tee_apinat(x, y)
                if soita_aani:
                    self.soita_tulivuorenpurkaus()
                return

    def saaret_leikkaa(self, x: int, y: int, saari: Tuple[int, int, int]) -> bool:
        """Tarkistaa leikkaako saaret ja palauttaa siitä boolean arvon.
        saari-listasta tallennetaan arvot x ja y muuttujiin sx sekä sy, 
        jonka jälkeen verrataan arvoja funktion argumentteihin."""
        sx, sy, _ = saari
        return (x < sx + self.saari_koko and x + self.saari_koko > sx and y < sy + self.saari_koko and y + self.saari_koko > sy)

    def soita_tulivuorenpurkaus(self) -> None:
        """Soittaa tulivuorenpurkausäänen kutsuttaessa"""
        winsound.Beep(200,500)

    def tee_apinat(self, x: int, y: int) -> None:
        """Luo kymmenen apinaa saarelle."""
        for _ in range(10):
            apina_x: int = x + random.randint(5, self.saari_koko - 5)
            apina_y: int = y + random.randint(5, self.saari_koko - 5)
            apina_id = self.canvas.create_oval(apina_x, apina_y, apina_x + 5, apina_y + 5, fill='brown')
            self.apinat.append({
                'id': apina_id,
                'x': apina_x,
                'y': apina_y,
                'saari': (x, y)
            })
        self.paivita_apina_maara()

    def apinoiden_elama(self) -> None:
        """Simuloi apinoiden elämää ja mahdollisuutta kuolla nauruun.
        Laskee 1% todennäköisyyden kuolla."""
        while True:
            for apina in self.apinat:
                if random.random() < 0.01:
                    self.apina_kuolee_nauruun(apina)
            time.sleep(10)

    def uivien_apinoiden_elama(self) -> None:
        while True:
            for apina in self.uivat_apinat.copy():
                if random.random() < 0.01:
                    self.apina_syodaan(apina)
                elif apina['uintimatka'] > 500:
                    self.apina_palaa_saarelle(apina)
            time.sleep(1)
    
    def apina_kuolee_nauruun(self, apina: Dict[str, Any]) -> None:
        self.canvas.delete(apina['id'])
        self.apinat.remove(apina)
        # Kolme piippausta, ha-ha-ha
        for _ in range(3):
            winsound.Beep(3000, 50)
        print(f"Apina-{apina['id']} kuoli nauruun!")
        self.paivita_apina_maara()

    def apina_syodaan(self, apina: Dict[str, Any]) -> None:
        """Funktio käsittelee apinoiden syödyksi tulemista.
        Poistaa apinan listasta sekä pelipohjalta ja soittaa äänen merkiksi."""
        self.canvas.delete(apina['id'])
        self.uivat_apinat.remove(apina)
        winsound.Beep(100, 1000)
        print(f"Apina-{apina['id']} tuli syödyksi! Hän kerkesi uida {int(apina['uintimatka'])} yksikköä!")
        self.paivita_apina_maara()

    def laita_apina_uimaan(self, apina: Dict[str, Any]) -> None:
        self.apinat.remove(apina)

        suunta = random.uniform(0, 2 * math.pi)
        nopeus = random.uniform(1, 3)

        apina['suunta'] = suunta
        apina['nopeus'] = nopeus
        apina['uintimatka'] = 0

        self.uivat_apinat.append(apina)

        self.liikuta_apinaa(apina)
        self.paivita_apina_maara()

    def liikuta_apinaa(self, apina: Dict[str, Any]) -> None:
        """Liikuttaa apinaa merellä ja jatkaa liikettä, kunnes apina tulee syödyksi."""
        if apina in self.uivat_apinat:
            dx = apina['nopeus'] * math.cos(apina['suunta'])
            dy = apina['nopeus'] * math.sin(apina['suunta'])

            uusi_x = apina['x'] + dx
            uusi_y = apina['y'] + dy

            # Tarkistetaan, pysyykö apina canvas-alueella
            if 0 <= uusi_x <= self.canvas.winfo_width() and 0 <= uusi_y <= self.canvas.winfo_height():
                self.canvas.move(apina['id'], dx, dy)
                apina['x'] = uusi_x
                apina['y'] = uusi_y
                apina['uintimatka'] += math.sqrt(dx**2 + dy**2)
            else:
                # Jos apina yrittää uida ulos canvas-alueelta, käännetään sen suuntaa
                apina['suunta'] = random.uniform(0, 2 * math.pi)

            # Muutetaan suuntaa satunnaisesti aika ajoin
            if random.random() < 0.1:
                apina['suunta'] += random.uniform(-math.pi/4, math.pi/4)

            # Jatketaan liikettä 100ms kuluttua
            self.master.after(100, self.liikuta_apinaa, apina)
        else:
            # Apina on tullut syödyksi, joten lopetetaan sen liikuttaminen
            pass

    def laheta_apina_uimaan(self) -> None:
        """Lähettää satunnaisen apinan uimaan."""
        if self.apinat:
            apina = random.choice(self.apinat)
            self.laita_apina_uimaan(apina)
            print(f"Apina-{apina['id']} lähti uimaan!")
        else:
            print("Ei apinoita lähetettäväksi uimaan!")

    def apinan_aanet(self) -> None:
        """Tuottaa apinoiden ääniä jatkuvasti säikeessä.
        Ääniä ei tuoteta, jos saaria ei ole olemassa."""
        while True:
            if self.saaret and self.apinat:
                for _ in range(min(len(self.saaret), 10)):
                    taajuus: int = random.randint(400, 2000)
                    for _ in range(2):
                        winsound.Beep(taajuus, 200)
            time.sleep(10)

    def tyhjenna_meri(self) -> None:
        """Tyhjentää merestä saaret sekä apinat, jonka jälkeen alustaa listat tyhjiksi."""
        for _, _, saari in self.saaret:
            self.canvas.delete(saari)
        for apina in self.apinat:
            self.canvas.delete(apina['id'])
        for apina in self.uivat_apinat:
            self.canvas.delete(apina['id'])
        self.saaret = []
        self.apinat = []
        self.uivat_apinat = []
        print("Meri on tyhjennetty saarista ja apinoista.")
        self.paivita_apina_maara()

    def tee_10_saarta(self) -> None:
        """Tekee kymmenen saarta kerralla. Tyhjentää ensin meren saarista ja apinoista."""
        self.tyhjenna_meri()
        for _ in range(self.max_saaret):
            self.tee_saari(soita_aani=False)
        self.canvas.update()
        self.soita_tulivuorenpurkaus()

    def apina_palaa_saarelle(self, apina: Dict[str, Any]) -> None:
        """Palauttaa apinan lähimmälle saarelle"""
        lahin_saari = min(self.saaret, key=lambda s: math.hypot(s[0] - apina['x'], s[1] - apina['y']))
        apina['x'] = lahin_saari[0] + random.randint(5, self.saari_koko - 5)
        apina['y'] = lahin_saari[1] + random.randint(5, self.saari_koko - 5)
        self.canvas.coords(apina['id'], apina['x'], apina['y'], apina['x'] + 5, apina['y'] + 5)
        self.uivat_apinat.remove(apina)
        self.apinat.append(apina)
        print(f"Apina-{apina['id']} palasi saarelle!")
        self.paivita_apina_maara()

    def paivita_apina_maara(self) -> None:
        """Päivittää apinoiden kokonaismäärän näytölle."""
        kokonaismaara = len(self.apinat) + len(self.uivat_apinat)
        self.apina_maara_var.set(f"Apinoita yhteensä: {kokonaismaara}")

root: tk.Tk = tk.Tk()
app: Saarisimulaattori = Saarisimulaattori(root)
root.mainloop()
