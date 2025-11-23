import os
from openai import OpenAI
from engine import PopulationGenerator 

# --- TU WPISZ SWÓJ KLUCZ (W CUDZYSŁOWIE!) ---
API_KEY = "" 

if "TU_WKLEJ" in API_KEY:
    print("❌ BŁĄD: Musisz wpisać swój klucz API w pliku main.py!")
    exit()

client = OpenAI(api_key=API_KEY)

def run_simulation():
    # --- TESTUJEMY NOWY PRODUKT ---
    product_name = "Kurs Inwestowania w Krypto 'Masterclass'"
    product_price = 2500.0
    
    print(f"🚀 START MASOWEJ SYMULACJI: {product_name} ({product_price} PLN)")

    # --- WCZYTYWANIE DANYCH Z PLIKU CSV ---
    print(f"\n📂 Wczytuję bazę klientów z pliku 'klienci.csv'...")
    # Tutaj wywołujemy nową funkcję, która czyta plik!
    population = PopulationGenerator.create_from_csv("klienci.csv")
    
    if not population:
        print("❌ Nie udało się wczytać klientów. Sprawdź czy plik klienci.csv istnieje.")
        return

    print(f"✅ Wczytano {len(population)} unikalnych profili klientów.\n")
    
    # --- MASOWA ANALIZA ---
    buy_count = 0
    
    for agent in population:
        print(f"👤 {agent.name} analizuje...")
        decision = agent.evaluate_product(product_name, product_price, client)
        
        status_icon = '✅' if decision['decision'] == 'BUY' else '❌'
        if decision['decision'] == 'BUY':
            buy_count += 1
            
        print(f"   {status_icon} Decyzja: {decision['decision']}")
        print(f"   💬 Opinia: {decision['reasoning']}")
        print("-" * 40)

    # --- RAPORT KOŃCOWY ---
    conversion = (buy_count / len(population)) * 100
    print(f"\n📊 WYNIK KOŃCOWY: {buy_count} na {len(population)} kupiło.")
    print(f"📈 Konwersja: {conversion}%")

if __name__ == "__main__":
    run_simulation()