import streamlit as st
import pandas as pd
from openai import OpenAI
from engine import PopulationGenerator
from fpdf import FPDF
import io

# --- FUNKCJA DO PDF (CLEANER) ---
def clean_text(text):
    """Usuwa polskie znaki dla prostego PDFa (zastępuje ą -> a)"""
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z',
        '✅': '[TAK]', '❌': '[NIE]', '⚠️': '[!]', '🦄': ''
    }
    text = str(text)
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf(product_name, price, conversion, revenue, advice, results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Tytuł
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=clean_text(f"Raport StartupAI: {product_name}"), ln=1, align='C')
    pdf.ln(10)
    
    # Wyniki Główne
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=clean_text(f"Cena produktu: {price} PLN"), ln=1)
    pdf.cell(200, 10, txt=clean_text(f"Konwersja: {conversion:.1f}%"), ln=1)
    pdf.cell(200, 10, txt=clean_text(f"Przewidywany Przychod: {revenue:,.0f} PLN"), ln=1)
    pdf.ln(10)
    
    # Porada AI
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Strategia Naprawcza (AI):", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=clean_text(advice))
    pdf.ln(10)
    
    # Tabela opinii
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Opinie Klientow:", ln=1)
    pdf.set_font("Arial", size=10)
    
    for r in results:
        decision = "[KUPIL]" if "TAK" in clean_text(r['Decyzja']) else "[ODRZUCIL]"
        line = f"{decision} {r['Klient']} ({r['Segment']}): {r['Powód']}"
        pdf.multi_cell(0, 8, txt=clean_text(line))
        pdf.ln(2)

    return pdf.output(dest='S').encode('latin-1')

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="StartupAI Enterprise", page_icon="🦄", layout="wide")

# --- STYLE CSS ---
st.markdown("""
<style>
    .stMetric {background-color: #f0f2f6; padding: 15px; border-radius: 10px;}
    .stAlert {padding: 20px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# --- PASEK BOCZNY ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=50)
    st.title("StartupAI 4.0")
    st.caption("Full Enterprise Suite")
    st.markdown("---")
    # --- INTELIGENTNE POBIERANIE KLUCZA ---
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ Klucz API załadowany automatycznie!")
    else:
        api_key = st.text_input("🔑 Wpisz Klucz OpenAI API:", type="password")
    st.markdown("---")
    uploaded_file = st.file_uploader("Wgraj plik CSV", type=["csv"])

# --- GŁÓWNY EKRAN ---
st.title("🦄 StartupAI: Raportowanie Enterprise")

col1, col2 = st.columns([2, 1])
with col1:
    product_name = st.text_input("Nazwa Produktu", "Kurs Inwestowania w Krypto")
with col2:
    product_price = st.number_input("Cena (PLN)", value=2500, step=50)

if st.button("🔥 URUCHOM ANALIZĘ", type="primary"):
    
    if not api_key:
        st.error("❌ Najpierw wpisz klucz API!")
        st.stop()
        
    if not uploaded_file:
        filename = "klienci.csv"
        try:
            population = PopulationGenerator.create_from_csv(filename)
            st.info(f"ℹ️ Używam domyślnej bazy: {filename}")
        except:
            st.error("Nie znaleziono pliku klienci.csv!")
            st.stop()
    else:
        with open("temp_upload.csv", "wb") as f:
            f.write(uploaded_file.getbuffer())
        population = PopulationGenerator.create_from_csv("temp_upload.csv")

    client = OpenAI(api_key=api_key)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    buy_count = 0
    rejections = [] 
    
    for i, agent in enumerate(population):
        status_text.text(f"🤖 Analizuję profil: {agent.name}...")
        decision = agent.evaluate_product(product_name, product_price, client)
        
        is_buy = decision['decision'] == 'BUY'
        if is_buy:
            buy_count += 1
        else:
            rejections.append(f"{agent.name} ({agent.segment.value}): {decision['reasoning']}")

        results.append({
            "Klient": agent.name,
            "Segment": agent.segment.value,
            "Decyzja": "✅ KUPIŁ" if is_buy else "❌ ODRZUCIŁ",
            "Powód": decision['reasoning'],
            "Zarobki": f"{agent.income_level} PLN"
        })
        progress_bar.progress((i + 1) / len(population))

    progress_bar.empty()
    status_text.empty()

    # --- WYNIKI ---
    st.divider()
    conversion = (buy_count / len(population)) * 100
    revenue = buy_count * product_price
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Decyzje", f"{buy_count} / {len(population)}")
    k2.metric("Konwersja", f"{conversion:.1f}%")
    k3.metric("Przychód", f"{revenue:,.0f} PLN")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.bar_chart(pd.DataFrame(results)["Decyzja"].value_counts())
    with c2:
        st.dataframe(pd.DataFrame(results), use_container_width=True)

    # --- AI CONSULTANT ---
    st.divider()
    st.subheader("🧠 Strategia i Raport")
    
    advice_text = "Produkt jest idealny. Brak uwag."
    if conversion < 100:
        with st.spinner("Generowanie strategii..."):
            prompt = f"""
            Produkt: "{product_name}" ({product_price} PLN).
            Powody odmowy: {rejections}
            Zaproponuj 1 konkretną zmianę (Pivot) i nową nazwę. Bez formatowania markdown, sam tekst.
            """
            advice = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            advice_text = advice.choices[0].message.content
            st.warning(advice_text)

    # --- GENEROWANIE PDF ---
    st.divider()
    st.success("✅ Analiza zakończona. Twój raport jest gotowy.")
    
    pdf_bytes = create_pdf(product_name, product_price, conversion, revenue, advice_text, results)
    
    st.download_button(
        label="📄 POBIERZ PEŁNY RAPORT PDF",
        data=pdf_bytes,
        file_name="StartupAI_Raport.pdf",
        mime="application/pdf",
        type="secondary"
    )