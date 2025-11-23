import streamlit as st
import pandas as pd
from openai import OpenAI
from engine import PopulationGenerator
from fpdf import FPDF
import io
import os

def clean_text(text):
    replacements = {'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z','✅':'[TAK]','❌':'[NIE]','⚠️':'[!]','🦄':''}
    text = str(text)
    for k, v in replacements.items(): text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf(product_name, price, unit, conversion, revenue, advice, results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=clean_text(f"Raport StartupAI: {product_name}"), ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    # ZMIANA: Dodajemy jednostkę do raportu
    pdf.cell(200, 10, txt=clean_text(f"Cena: {price} PLN / {unit}"), ln=1)
    pdf.cell(200, 10, txt=clean_text(f"Konwersja: {conversion:.1f}%"), ln=1)
    pdf.cell(200, 10, txt=clean_text(f"Przewidywany Przychod: {revenue:,.0f} PLN"), ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Strategia Naprawcza (AI):", ln=1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=clean_text(advice))
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Opinie Klientow:", ln=1)
    pdf.set_font("Arial", size=10)
    for r in results:
        decision = "[KUPIL]" if "TAK" in clean_text(r['Decyzja']) else "[ODRZUCIL]"
        line = f"{decision} {r['Klient']} ({r['Wiek']} lat, {r['Miasto']}): {r['Powód']}"
        pdf.multi_cell(0, 8, txt=clean_text(line))
        pdf.ln(2)
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="StartupAI Enterprise", page_icon="🦄", layout="wide")
st.markdown("""<style>.stMetric {background-color: #f0f2f6; padding: 15px; border-radius: 10px;} .stAlert {padding: 20px; border-radius: 10px;}</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=50)
    st.title("StartupAI 6.0")
    st.markdown("---")
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✅ Klucz API załadowany!")
    else:
        api_key = st.text_input("🔑 Wpisz Klucz OpenAI API:", type="password")
    st.markdown("---")
    st.subheader("👥 Grupa Badawcza")
    data_source = st.radio("Wybierz źródło:", ["Gotowe Bazy", "Wgraj własny plik"], index=0)
    target_file = None
    if data_source == "Gotowe Bazy":
        options = ["Mała (5 osób)"]
        if os.path.exists("baza_100.csv"): options.append("Średnia (100 osób)")
        if os.path.exists("baza_500.csv"): options.append("Duża (500 osób)")
        choice = st.selectbox("Wybierz wielkość próby:", options)
        if "5 osób" in choice: target_file = "klienci.csv"
        elif "100 osób" in choice: target_file = "baza_100.csv"
        elif "500 osób" in choice: target_file = "baza_500.csv"
    else:
        uploaded_file = st.file_uploader("Wgraj plik CSV", type=["csv"])
        if uploaded_file:
            with open("temp_upload.csv", "wb") as f: f.write(uploaded_file.getbuffer())
            target_file = "temp_upload.csv"

st.title("🦄 StartupAI: Symulator Rynku")

# --- SEKCJA PRODUKTU (ZMIENIONA) ---
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    product_name = st.text_input("Opis Produktu", "Wegańska Kiełbasa dla Górników")
with c2:
    product_price = st.number_input("Cena (PLN)", value=35, step=1)
with c3:
    # ZMIANA: Wybór jednostki
    product_unit = st.selectbox("Jednostka", ["sztuka", "kg", "litr", "para", "zestaw", "godzina", "miesiąc", "rok"])

if st.button("🔥 URUCHOM ANALIZĘ", type="primary"):
    if not api_key: st.error("Brak klucza API!"); st.stop()
    if not target_file: st.error("Brak bazy danych!"); st.stop()
    try:
        population = PopulationGenerator.create_from_csv(target_file)
    except: st.error("Błąd pliku bazy!"); st.stop()

    client = OpenAI(api_key=api_key)
    progress_bar = st.progress(0); status_text = st.empty()
    results = []; buy_count = 0; rejections = []
    total_agents = len(population)

    for i, agent in enumerate(population):
        status_text.text(f"🤖 [{i+1}/{total_agents}] Rozmawiam z: {agent.name}...")
        # ZMIANA: Przekazujemy jednostkę do silnika
        decision = agent.evaluate_product(product_name, product_price, product_unit, client)
        
        is_buy = decision['decision'] == 'BUY'
        if is_buy: buy_count += 1
        else: rejections.append(f"{agent.segment.value}: {decision['reasoning']}")
        
        results.append({
            "Klient": agent.name, "Wiek": agent.age, "Zawód": agent.job, "Miasto": agent.location,
            "Segment": agent.segment.value, "Decyzja": "✅ KUPIŁ" if is_buy else "❌ ODRZUCIŁ",
            "Powód": decision['reasoning'], "Zarobki": f"{agent.income_level} PLN"
        })
        progress_bar.progress((i + 1) / total_agents)

    progress_bar.empty(); status_text.empty()
    st.divider()
    conversion = (buy_count / total_agents) * 100
    revenue = buy_count * product_price
    k1, k2, k3 = st.columns(3)
    k1.metric("Decyzje", f"{buy_count} / {total_agents}")
    k2.metric("Konwersja", f"{conversion:.1f}%")
    k3.metric(f"Przychód (z 1 {product_unit})", f"{revenue:,.0f} PLN") # Info o jednostce
    
    c1, c2 = st.columns([1, 2])
    with c1: st.bar_chart(pd.DataFrame(results)["Decyzja"].value_counts())
    with c2: st.dataframe(pd.DataFrame(results), use_container_width=True)

    st.divider(); st.subheader("🧠 Strategia i Raport")
    advice_text = "Produkt jest idealny."
    if conversion < 100:
        with st.spinner("Generowanie strategii..."):
            prompt = f"Produkt: {product_name} ({product_price} PLN / {product_unit}). Odmowy: {rejections[:20]}. Zaproponuj pivot i nazwę."
            advice = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            advice_text = advice.choices[0].message.content
            st.warning(advice_text)

    st.divider(); st.success("✅ Analiza zakończona.")
    # ZMIANA: Przekazujemy jednostkę do PDF
    pdf_bytes = create_pdf(product_name, product_price, product_unit, conversion, revenue, advice_text, results)
    st.download_button(label="📄 POBIERZ PEŁNY RAPORT PDF", data=pdf_bytes, file_name="StartupAI_Raport.pdf", mime="application/pdf", type="secondary")