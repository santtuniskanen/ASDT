"""
Apinapeli Mk3 - Santtu Niskanen
"""
from typing import List, Tuple
import tkinter as tk
import winsound
import random
import time
import threading

class Saarisimulaattori:
    def __init__(self, master: tk.Tk) -> None:
        self.master: tk.Tk = master
        self.master.title("Saarisimulaattori")

        self.canvas: tk.Canvas = tk.Canvas(self.master, width=800, height=600, bg='blue')
        self.canvas.pack()

        self.saaret: List[Tuple[int, int, int]] = []
        self.apinat: List[int] = []
        self.saari_koko: int = 50

        self.tulivuori_nappi: tk.Button = tk.Button(self.master, text="Tulivuorenpurkaus", command=self.tee_saari)
        self.tulivuori_nappi.pack()

        self.tyhjenna_nappi: tk.Button = tk.Button(self.master, text="Tyhjennä meri", command=self.tyhjenna_meri)
        self.tyhjenna_nappi.pack()
        
        self.tee_10_saarta_nappi: tk.Button = tk.Button(self.master, text="Lisää 10 saarta", command=self.tee_10_saarta)
        self.tee_10_saarta_nappi.pack()

        threading.Thread(target=self.apinan_aanet, daemon=True).start()

    def tee_saari(self, soita_aani: bool = True) -> None:
        """Funktio tarkistaa ensin onko 'saaret' listassa jo kymmenen saarta. Tämän jälkeen funktio menee looppiin, jossa se luo satunnaisesti x ja y arvot ja tarkistaa leikkaako saari toisen saaren. Tämän jälkeen jatketaan saaren luomiseen ja lisätään se 'saaret' listaan.
        """
        if len(self.saaret) >= 10:
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
        saari-listasta tallennetaan arvot x ja y muuttujiin sx sekä sy, jonka jälkeen verrataan arvoja funktion argumentteihin.
        """
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
            self.apinat.append(apina_id)

    def apinan_aanet(self) -> None:
        """Tuottaa apinoiden ääniä jatkuvasti säikeessä. Ääniä ei tuoteta, jos saaria ei ole olemassa."""
        while True:
            if self.saaret:
                for _ in range(min(len(self.saaret), 10)):
                    taajuus: int = random.randint(400, 2000)
                    winsound.Beep(taajuus, 100)
            time.sleep(10)

    def tyhjenna_meri(self) -> None:
        """Tyhjentää merestä saaret sekä apinat, jonka jälkeen alustaa listat tyhjiksi."""
        for _, _, saari in self.saaret:
            self.canvas.delete(saari)
        for apina in self.apinat:
            self.canvas.delete(apina)
        self.saaret = []
        self.apinat = []
    
    def tee_10_saarta(self) -> None:
        """Tekee kymmenen saarta kerralla. Tyhjentää ensin meren."""
        self.tyhjenna_meri()
        for _ in range(10):
            self.tee_saari(soita_aani=False)
        self.canvas.update()
        self.soita_tulivuorenpurkaus()

root: tk.Tk = tk.Tk()
app: Saarisimulaattori = Saarisimulaattori(root)
root.mainloop()
