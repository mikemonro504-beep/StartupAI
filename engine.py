import json
import csv
from typing import List, Dict
from enum import Enum
from dataclasses import dataclass
import openai

# --- MODEL PSYCHOLOGICZNY ---
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
            if e.value == label:
                return e
        return MarketSegment.UNKNOWN

# --- KLASA AGENTA ---
class DigitalTwin:
    def __init__(self, id: int, name: str, segment: MarketSegment, traits: PersonalityTraits, income_level: int):
        self.id = id
        self.name = name
        self.segment = segment
        self.traits = traits
        self.income_level = income_level
        self.memory = [] 
        
    def _generate_system_prompt(self) -> str:
        base_prompt = f"""
        Jesteś symulacją konsumenta. NIE jesteś asystentem AI.
        Nazywasz się {self.name}. Jesteś z segmentu: {self.segment.value}.
        Twoje zarobki roczne to: {self.income_level} PLN.
        
        TWOJA OSOBOWOŚĆ (Skala 0-1):
        - Otwartość: {self.traits.openness} (Czy lubisz nowości?)
        - Sumienność: {self.traits.conscientiousness} (Czy analizujesz szczegóły?)
        - Ugodowość: {self.traits.agreeableness} (Czy jesteś miły czy krytyczny?)
        - Neurotyczność: {self.traits.neuroticism} (Czy boisz się ryzyka?)
        
        Decyzje podejmujesz TYLKO na podstawie tych cech.
        """
        return base_prompt

    def evaluate_product(self, product_description: str, price: float, client_openai) -> Dict:
        prompt = f"""
        Produkt: {product_description}
        Cena: {price} PLN
        
        Przeanalizuj to. Odpowiedz TYLKO w formacie JSON:
        {{
            "decision": "BUY" lub "NO_BUY",
            "score": (ocena 1-100),
            "reasoning": "Krótkie uzasadnienie w 1 zdaniu (max 15 słów)",
            "key_objection": "Główna obiekcja lub zaleta"
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
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            return {"decision": "ERROR", "score": 0, "reasoning": str(e), "key_objection": "Błąd API"}

# --- NOWY GENERATOR Z PLIKU CSV ---
class PopulationGenerator:
    @staticmethod
    def create_from_csv(filename: str) -> List[DigitalTwin]:
        population = []
        try:
            with open(filename, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Tworzymy cechy osobowości z pliku
                    traits = PersonalityTraits(
                        openness=float(row['openness']),
                        conscientiousness=float(row['conscientiousness']),
                        extraversion=float(row['extraversion']),
                        agreeableness=float(row['agreeableness']),
                        neuroticism=float(row['neuroticism'])
                    )
                    
                    # Tworzymy agenta
                    agent = DigitalTwin(
                        id=int(row['id']),
                        name=row['name'],
                        segment=MarketSegment.from_str(row['segment']),
                        traits=traits,
                        income_level=int(row['income'])
                    )
                    population.append(agent)
        except FileNotFoundError:
            print(f"❌ BŁĄD: Nie znaleziono pliku {filename}!")
        return population