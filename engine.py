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

    # ZMIANA: Dodaliśmy argument 'unit' (jednostka)
    def evaluate_product(self, product_description: str, price: float, unit: str, client_openai) -> Dict:
        prompt = f"""
        Produkt: {product_description}
        Cena: {price} PLN za {unit}
        
        Oceń zakup w formacie JSON: decision (BUY/NO_BUY), reasoning (krótko), key_objection.
        Bierz pod uwagę czy cena za taką jednostkę ({unit}) jest rynkowa.
        """
        try:
            response = client_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": self._generate_system_prompt()}, {"role": "user", "content": prompt}],
                response_format={ "type": "json_object" } 
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"decision": "ERROR", "reasoning": str(e)}

# --- GENERATOR ---
class PopulationGenerator:
    @staticmethod
    def create_from_csv(filename: str) -> List[DigitalTwin]:
        population = []
        try:
            with open(filename, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
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
        except Exception as e:
            print(f"❌ Błąd: {e}")
        return population