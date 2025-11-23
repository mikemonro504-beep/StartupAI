import csv
import random
import time

# --- KONFIGURACJA ---
WIELKOSCI_BAZ = [100, 500, 1000] 

# --- DANE DEMOGRAFICZNE ---
imiona = ["Anna", "Piotr", "Krzysztof", "Maria", "Agnieszka", "Tomasz", "Paweł", "Ewa", "Michał", "Kasia", "Jan", "Małgosia", "Bartek", "Ola", "Zofia", "Adam", "Magda", "Kamil", "Natalia", "Rafał"]
nazwiska = ["Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski", "Zieliński", "Szymański", "Woźniak", "Mazur", "Krawczyk"]

miasta = ["Warszawa", "Kraków", "Wieś (Mazowieckie)", "Wrocław", "Poznań", "Wieś (Podkarpacie)", "Gdańsk", "Małe miasteczko", "Łódź", "Katowice", "Wieś (Wielkopolska)"]

# Logika zawodów i wieku dla każdego segmentu
segmenty_logika = {
    "Gen Z Student": {
        "wiek_min": 19, "wiek_max": 25,
        "zawody": ["Student", "Stażysta w korpo", "Kelner", "Grafik Freelancer", "Barista", "Tutor", "Bezrobotny"],
        "min_zarobki": 0, "max_zarobki": 4500
    },
    "Corporate Professional": {
        "wiek_min": 28, "wiek_max": 50,
        "zawody": ["Manager Projektu", "Programista", "Dyrektor Finansowy", "Prawnik", "HR Manager", "Analityk Danych", "Marketingowiec"],
        "min_zarobki": 8000, "max_zarobki": 40000
    },
    "Senior Citizen": {
        "wiek_min": 65, "wiek_max": 85,
        "zawody": ["Emerytowany Nauczyciel", "Emerytowany Górnik", "Emerytowana Księgowa", "Emeryt Wojskowy", "Emeryt"],
        "min_zarobki": 2200, "max_zarobki": 5500
    },
    "Tech Early Adopter": {
        "wiek_min": 25, "wiek_max": 40,
        "zawody": ["Startup Founder", "Inżynier AI", "Youtuber", "Trader Krypto", "Product Designer", "Bloger Tech"],
        "min_zarobki": 6000, "max_zarobki": 25000
    }
}

print("⚙️ Uruchamiam zaawansowaną fabrykę danych...")

for ilosc in WIELKOSCI_BAZ:
    nazwa_pliku = f"baza_{ilosc}.csv"
    
    with open(nazwa_pliku, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Rozszerzony nagłówek
        writer.writerow(["id", "name", "segment", "income", "age", "job", "location", "family_size", "openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"])

        for i in range(1, ilosc + 1):
            # Losujemy klucz segmentu
            seg_nazwa = random.choice(list(segmenty_logika.keys()))
            dane_seg = segmenty_logika[seg_nazwa]
            
            imie = f"{random.choice(imiona)} {random.choice(nazwiska)}"
            wiek = random.randint(dane_seg["wiek_min"], dane_seg["wiek_max"])
            zawod = random.choice(dane_seg["zawody"])
            lokalizacja = random.choice(miasta)
            zarobki = random.randint(dane_seg["min_zarobki"], dane_seg["max_zarobki"])
            
            # Wielkość rodziny (zależna trochę od wieku)
            if wiek < 22: rodzina = 1
            elif wiek > 65: rodzina = random.randint(1, 2)
            else: rodzina = random.randint(1, 5)

            writer.writerow([
                i, imie, seg_nazwa, zarobki, wiek, zawod, lokalizacja, rodzina,
                round(random.random(), 2), round(random.random(), 2), 
                round(random.random(), 2), round(random.random(), 2), round(random.random(), 2)
            ])
    
    print(f"✅ Wygenerowano: {nazwa_pliku} ({ilosc} szczegółowych profili).")

print("\n🎉 Baza zaktualizowana!")