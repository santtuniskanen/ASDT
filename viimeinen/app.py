"""
Apinapeli Mk3 - Santtu Niskanen
"""
from typing import Any, List, Dict, Tuple, Set
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
        self.saari_nimet: Dict[int, str] = {}
        self.matkailutietoiset_saaret: Set[int] = set()

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
        self.master.after(10000, self.laheta_automaattisesti_uimaan)

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
                saari_id: int = self.canvas.create_oval(x, y, x + self.saari_koko, y + self.saari_koko, fill='green')
                saari_nimi = f"S{len(self.saaret) + 1}"
                self.saari_nimet[saari_id] = saari_nimi
                teksti = self.canvas.create_text(x + self.saari_koko // 2, y + self.saari_koko // 2, text=f"{saari_nimi}\n0", font=("Arial", 10, "bold"))
                self.saaret.append((x, y, saari_id, teksti))
                self.tee_apinat(x, y)
                
                if saari_nimi == "S1":
                    self.lisaa_laiturit(x, y, saari_id)
                    self.matkailutietoiset_saaret.add(saari_id)
                
                if soita_aani:
                    self.soita_tulivuorenpurkaus()
                return

    def lisaa_laiturit(self, x: int, y: int, saari_id: int) -> None:
        """Lisää laiturit saarelle, kun saaresta tulee matkailutietoinen."""
        laituri_pituus = 20
        laituri_leveys = 5
        keskipiste_x = x + self.saari_koko // 2
        keskipiste_y = y + self.saari_koko // 2

        self.canvas.create_rectangle(keskipiste_x - laituri_leveys // 2, y - laituri_pituus,
                                    keskipiste_x + laituri_leveys // 2, y, fill='brown')
        self.canvas.create_rectangle(x + self.saari_koko, keskipiste_y - laituri_leveys // 2,
                                    x + self.saari_koko + laituri_pituus, keskipiste_y + laituri_leveys // 2, fill='brown')
        self.canvas.create_rectangle(keskipiste_x - laituri_leveys // 2, y + self.saari_koko,
                                    keskipiste_x + laituri_leveys // 2, y + self.saari_koko + laituri_pituus, fill='brown')
        self.canvas.create_rectangle(x - laituri_pituus, keskipiste_y - laituri_leveys // 2,
                                    x, keskipiste_y + laituri_leveys // 2, fill='brown')

    def laheta_automaattisesti_uimaan(self) -> None:
        """Lähettää apinan automaattisesti uimaan 10 sekunnin välein.
        Saarella täytyy olla matkailutietoisuus automaattiseen lähtöön."""
        for saari in self.saaret:
            x, y, saari_id, _ = saari
            if saari_id in self.matkailutietoiset_saaret:
                saaren_apinat = [apina for apina in self.apinat if apina['saari'] == (x, y)]
                if saaren_apinat:
                    apina = random.choice(saaren_apinat)
                    self.laita_apina_uimaan(apina)
        self.master.after(10000, self.laheta_automaattisesti_uimaan)

    def paivita_saaren_apinamaara(self, saari: Tuple[int, int, int, int]) -> None:
        x, y, saari_id, teksti = saari
        apina_maara = sum(1 for apina in self.apinat if apina['saari'] == (x, y))
        self.canvas.itemconfig(teksti, text=f"{self.saari_nimet[saari_id]}\n{apina_maara}")

    def saaret_leikkaa(self, x: int, y: int, saari: Tuple[int, int, int]) -> bool:
        """Tarkistaa leikkaako saaret ja palauttaa siitä boolean arvon.
        saari-listasta tallennetaan arvot x ja y muuttujiin sx sekä sy, 
        jonka jälkeen verrataan arvoja funktion argumentteihin."""
        sx, sy, _, _ = saari
        return (x < sx + self.saari_koko and x + self.saari_koko > sx and
                y < sy + self.saari_koko and y + self.saari_koko > sy)

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
        saari = next(s for s in self.saaret if s[0] == x and s[1] == y)
        self.paivita_saaren_apinamaara(saari)
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
        """Funktio, joka käsittelee apinan elämää vedessä. 
        Funktio toimii sekunnin viiveellä, ja apinalla on 1% mahdollisuus 
        tulla hain syömäksi. Jos apina ei kuole, ja apinan uintimatka 
        ylittää 500 yksikköä, palaa apina saarelle."""
        while True:
            for apina in self.uivat_apinat.copy():
                if random.random() < 0.01:
                    self.apina_syodaan(apina)
                elif apina['uintimatka'] > 500:
                    self.apina_palaa_saarelle(apina)
            time.sleep(1)
    
    def apina_kuolee_nauruun(self, apina: Dict[str, Any]) -> None:
        """Kutsutaan silloin, kun apinalle käy kehnosti, ja se kuolee nauruun. 
        Apina poistetaan listalta ja canvakselta. 
        Lopussa päästetään kimeät kolme piippausta indikoimaan 
        liian äkäistä naurua, johon apina kuolee."""
        self.canvas.delete(apina['id'])
        self.apinat.remove(apina)
        saari = next(s for s in self.saaret if s[0] == apina['saari'][0] and s[1] == apina['saari'][1])
        self.paivita_saaren_apinamaara(saari)
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
        """Laittaa apinan uimaan kutsuttaessa. Poistaa apinan saarelta 
        sekä lisää sen uiviin apinoihin. Samalla apinalle annetaan 
        suunta ja nopeus, sekä alustetaan uintimatka."""
        self.apinat.remove(apina)
        saari = next(s for s in self.saaret if s[0] == apina['saari'][0] and s[1] == apina['saari'][1])
        self.paivita_saaren_apinamaara(saari)

        suunta = random.uniform(0, 2 * math.pi)
        nopeus = random.uniform(1, 3)

        apina['suunta'] = suunta
        apina['nopeus'] = nopeus
        apina['uintimatka'] = 0

        self.uivat_apinat.append(apina)

        self.liikuta_apinaa(apina)
        self.paivita_apina_maara()

    def liikuta_apinaa(self, apina: Dict[str, Any]) -> None:
        """Liikuttaa apinaa merellä ja jatkaa liikettä, kunnes apina tulee syödyksi
        tai pääsee saarelle.
        
        Funktiossa tarkistetaan, pysyykö apina canvas alueella. 
        Jos apina menee alueen yli, apinan suunta käännetään. 
        Muuten apinan suuntaa muutetaan satunnaisesti, ja funktio päättyy, 
        kun apina on tullut syödyksi, tai palaa saarelle.
        """
        if apina in self.uivat_apinat:
            dx = apina['nopeus'] * math.cos(apina['suunta'])
            dy = apina['nopeus'] * math.sin(apina['suunta'])

            uusi_x = apina['x'] + dx
            uusi_y = apina['y'] + dy

            if 0 <= uusi_x <= self.canvas.winfo_width() and 0 <= uusi_y <= self.canvas.winfo_height():
                self.canvas.move(apina['id'], dx, dy)
                apina['x'] = uusi_x
                apina['y'] = uusi_y
                apina['uintimatka'] += math.sqrt(dx**2 + dy**2)
            else:
                apina['suunta'] = random.uniform(0, 2 * math.pi)

            if random.random() < 0.1:
                apina['suunta'] += random.uniform(-math.pi/4, math.pi/4)

            self.master.after(100, self.liikuta_apinaa, apina)
        else:
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
        """Tyhjentää merestä saaret sekä apinat, 
        jonka jälkeen alustaa listat tyhjiksi."""
        for _, _, saari, teksti in self.saaret:
            self.canvas.delete(saari)
            self.canvas.delete(teksti)
        for apina in self.apinat:
            self.canvas.delete(apina['id'])
        for apina in self.uivat_apinat:
            self.canvas.delete(apina['id'])
        self.saaret = []
        self.apinat = []
        self.uivat_apinat = []
        self.saari_nimet = {}
        self.matkailutietoiset_saaret = set()
        print("Meri on tyhjennetty saarista ja apinoista.")
        self.paivita_apina_maara()

    def tee_10_saarta(self) -> None:
        """Tekee kymmenen saarta kerralla. Tyhjentää ensin meren 
        saarista ja apinoista.
        Soittaa kerran tulivuorenpurkausäänen."""
        self.tyhjenna_meri()
        for _ in range(self.max_saaret):
            self.tee_saari(soita_aani=False)
        self.canvas.update()
        self.soita_tulivuorenpurkaus()

    def apina_palaa_saarelle(self, apina: Dict[str, Any]) -> None:
        """Laskee lähimmän saaren etäisyyden apinasta käyttämällä math.hypot funktiota
        laskeakseen etäisyyden pisteiden välillä. 
        Sen jälkeen poistaa apinan uivat apinat listasta sekä lisää 
        apinan apinat listaan kyseiselle saarelle ja päivittää luvun.
        
        Jos apinan saari_id vastaa saarta, joka on matkailutietoinen,
        tulee uudesta saaresta myös matkailutietoinen.
        """
        lahin_saari = min(self.saaret, key=lambda s: math.hypot(s[0] - apina['x'], s[1] - apina['y']))
        x, y, saari_id, _ = lahin_saari
        apina['x'] = x + random.randint(5, self.saari_koko - 5)
        apina['y'] = y + random.randint(5, self.saari_koko - 5)
        apina['saari'] = (x, y)
        self.canvas.coords(apina['id'], apina['x'], apina['y'], apina['x'] + 5, apina['y'] + 5)
        self.uivat_apinat.remove(apina)
        self.apinat.append(apina)
        self.paivita_saaren_apinamaara(lahin_saari)
        
        if saari_id not in self.matkailutietoiset_saaret:
            self.matkailutietoiset_saaret.add(saari_id)
            self.lisaa_laiturit(x, y, saari_id)
            print(f"Saari {self.saari_nimet[saari_id]} on nyt matkailutietoinen!")
        
        print(f"Apina-{apina['id']} palasi saarelle {self.saari_nimet[saari_id]}!")
        self.paivita_apina_maara()

    def paivita_apina_maara(self) -> None:
        """Päivittää apinoiden kokonaismäärän näytölle."""
        kokonaismaara = len(self.apinat) + len(self.uivat_apinat)
        self.apina_maara_var.set(f"Apinoita yhteensä: {kokonaismaara}")


root: tk.Tk = tk.Tk()
app: Saarisimulaattori = Saarisimulaattori(root)
root.mainloop()
