import json
import csv
from typing import List, Dict
from enum import Enum
from dataclasses import dataclass
import openai

# --- MODEL ---
@dataclass
class PersonalityTraits:
    openness: float        
    conscientiousness: float
    extraversion: float    
    agreeableness: float   
    neuroticism: float     

class MarketSegment(Enum):
    GEN_Z_STUDENT = "Gen Z Student"
    CORPORATE_PRO = "Corporate Professional"
    SENIOR_CITIZEN = "Senior Citizen"
    TECH_EARLY_ADOPTER = "Tech Early Adopter"
    UNKNOWN = "Nieznany"

    @staticmethod
    def from_str(label):
        for e in MarketSegment:
            if e.value == label: return e
        return MarketSegment.UNKNOWN

# --- AGENT ---
class DigitalTwin:
    def __init__(self, id: int, name: str, segment: MarketSegment, traits: PersonalityTraits, 
                 income_level: int, age: int, job: str, location: str, family_size: int):
        self.id = id
        self.name = name
        self.segment = segment
        self.traits = traits
        self.income_level = income_level
        self.age = age
        self.job = job
        self.location = location
        self.family_size = family_size
        
    def _generate_system_prompt(self) -> str:
        return f"""
        Jesteś symulacją konsumenta.
        Imię: {self.name}, Wiek: {self.age}, Zawód: {self.job}, Miasto: {self.location}.
        Zarobki: {self.income_level} PLN. Rodzina: {self.family_size} osób.
        Segment: {self.segment.value}.
        Cechy (0-1): Otwartość {self.traits.openness}, Sumienność {self.traits.conscientiousness}, Ugodowość {self.traits.agreeableness}.
        Decyduj realistycznie.
        """

    def evaluate_product(self, product_description: str, price: float, client_openai) -> Dict:
        print(f"📞 Dzwonię do OpenAI w sprawie: {self.name}...") # <<< NOWY PRINT
        prompt = f"""
        Produkt: {product_description}
        Cena: {price} PLN
        Decyzja (JSON):
        {{
            "decision": "BUY" lub "NO_BUY",
            "score": (0-100),
            "reasoning": "Krótkie uzasadnienie",
            "key_objection": "Główna przeszkoda lub zaleta"
        }}
        """
        try:
            response = client_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self._generate_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" } 
            )
            print(f"✅ Otrzymałem odpowiedź dla: {self.name}") # <<< NOWY PRINT
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ BŁĄD API dla {self.name}: {e}") # <<< NOWY PRINT
            return {"decision": "ERROR", "reasoning": str(e)}
# --- GENERATOR (WERSJA GŁOŚNA) ---
class PopulationGenerator:
    @staticmethod
    def create_from_csv(filename: str) -> List[DigitalTwin]:
        population = []
        print(f"--- DEBUG: Próbuję otworzyć plik: {filename} ---")
        
        try:
            with open(filename, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Sprawdźmy nagłówki
                print(f"--- DEBUG: Znalezione kolumny: {reader.fieldnames}")
                
                for i, row in enumerate(reader):
                    try:
                        traits = PersonalityTraits(
                            openness=float(row['openness']),
                            conscientiousness=float(row['conscientiousness']),
                            extraversion=float(row['extraversion']),
                            agreeableness=float(row['agreeableness']),
                            neuroticism=float(row['neuroticism'])
                        )
                        
                        agent = DigitalTwin(
                            id=int(row['id']),
                            name=row['name'],
                            segment=MarketSegment.from_str(row['segment']),
                            traits=traits,
                            income_level=int(row['income']),
                            age=int(row['age']),
                            job=row['job'],
                            location=row['location'],
                            family_size=int(row['family_size'])
                        )
                        population.append(agent)
                    except KeyError as e:
                        print(f"❌ BŁĄD w wierszu {i}: Brakuje kolumny {e}! Sprawdź plik CSV.")
                    except ValueError as e:
                        print(f"❌ BŁĄD w wierszu {i}: Zły format liczby! {e}")
                        
        except FileNotFoundError:
            print(f"❌ BŁĄD KRYTYCZNY: Nie znaleziono pliku {filename}!")
            
        print(f"--- DEBUG: Załadowano poprawnie {len(population)} osób ---")
        return population