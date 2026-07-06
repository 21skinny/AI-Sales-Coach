import streamlit as st
from groq import Groq
import re

# Konfiguracja okna aplikacji - szeroki układ
st.set_page_config(page_title="AI Sales Coach - Pro Edition", layout="wide", initial_sidebar_state="expanded")

# BEZPIECZEŃSTWO: Pobieranie klucza z ukrytego sejfu chmury (Secrets)
KLUCZ_API = st.secrets["GROQ_API_KEY"]

# --- PAMIĘĆ APLIKACJI (SESSION STATE) ---
if "analiza_nieruchomosci" not in st.session_state:
    st.session_state.analiza_nieruchomosci = None
if "pytania_spin" not in st.session_state:
    st.session_state.pytania_spin = "Wklej ogłoszenie po lewej stronie i wygeneruj strategię, aby przygotować pytania SPIN."
if "szansa_na_spotkanie" not in st.session_state:
    st.session_state.szansa_na_spotkanie = 10
if "liczba_obiekcji" not in st.session_state:
    st.session_state.liczba_obiekcji = 0
if "ostatnia_odpowiedz" not in st.session_state:
    st.session_state.ostatnia_odpowiedz = "Czekam na pierwszą obiekcję..."
if "historia_rozmowy" not in st.session_state:
    st.session_state.historia_rozmowy = [] 

def pobierz_klienta_ai():
    if not KLUCZ_API:
        st.error("Brak konfiguracji klucza API w chmurze!")
        return None
    return Groq(api_key=KLUCZ_API)

# --- BOCZNY PASEK (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Baza Danych")
    st.markdown("Przygotuj system przed wykonaniem połączenia.")
    
    opis = st.text_area("Treść ogłoszenia (Mieszkanie):", height=200, placeholder="Wklej tutaj treść ogłoszenia...")
    
    if st.button("🔥 GENERUJ STRATEGIĘ", use_container_width=True):
        client = pobierz_klienta_ai()
        if client and opis:
            with st.spinner("Przetwarzanie danych..."):
                try:
                    prompt_analizy = f"""Jesteś analitykiem rynku nieruchomości. Przeanalizuj to ogłoszenie: '{opis}'
                    Wyciągnij w punktach: 1. Główne atuty 2. Słabe punkty (pole do negocjacji) 3. Krótka strategia."""
                    
                    response_analiza = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt_analizy}],
                        max_tokens=400
                    )
                    st.session_state.analiza_nieruchomosci = response_analiza.choices[0].message.content
                    
                    prompt_spin = f"""Jesteś elitarnym trenerem sprzedaży nieruchomości. Na podstawie tego ogłoszenia mieszkania: '{opis}'
                    Zbuduj dokładnie 3 genialne, otwarte pytania w metodologii SPIN Selling (Sytuacja, Problem, Implikacja, Potrzeba), 
                    które agent może zadać właścicielowi na początku rozmowy. Zwracaj się do rozmówcy na 'Pan/Pani/Państwo'."""

                    response_spin = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt_spin}],
                        max_tokens=400
                    )
                    st.session_state.pytania_spin = response_spin.choices[0].message.content
                    
                    st.session_state.szansa_na_spotkanie = 15
                    st.session_state.liczba_obiekcji = 0
                    st.session_state.historia_rozmowy = []
                except Exception as e:
                    st.error(f"Błąd analizy: {e}")

    if st.session_state.analiza_nieruchomosci:
        st.success("Strategia gotowa.")
        with st.expander("Podgląd Strategii"):
            st.write(st.session_state.analiza_nieruchomosci)

# --- GŁÓWNY EKRAN ---
st.title("🎙️ AI Sales Coach - Live Dashboard")

m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="Szansa na spotkanie (AI ocena)", value=f"{st.session_state.szansa_na_spotkanie}%")
with m2:
    st.metric(label="Przepracowane obiekcje", value=st.session_state.liczba_obiekcji)
with m3:
    st.metric(label="Status relacji", value="Wysokie zaangażowanie" if st.session_state.szansa_na_spotkanie > 50 else "Badanie potrzeb")

st.divider()

st.subheader("🟡 Koło Ratunkowe: Pytania SPIN do zadania na początku rozmowy")
st.warning(st.session_state.pytania_spin)

st.divider()

# ROZBUDOWANA SIATKA OBIEKCJI (3x3)
st.subheader("🔥 Właściciel rzuca obiekcję w słuchawkę:")
r1_col1, r1_col2, r1_col3 = st.columns(3)
r2_col1, r2_col2, r2_col3 = st.columns(3)
r3_col1, r3_col2, r3_col3 = st.columns(3)

obiekcja_kliknieta = None
nazwa_przycisku = ""

with r1_col1:
    if st.button("🚨 Mam już agencję", use_container_width=True): 
        obiekcja_kliknieta = "Mam już spisaną umowę z inną agencją nieruchomości."
        nazwa_przycisku = "Mam już agencję"
with r1_col2:
    if st.button("🚨 Prowizja za wysoka", use_container_width=True): 
        obiekcja_kliknieta = "Wasza prowizja jest zdecydowanie za wysoka, inni biorą mniej."
        nazwa_przycisku = "Prowizja za wysoka"
with r1_col3:
    if st.button("🚨 Sprzedam sam", use_container_width=True): 
        obiekcja_kliknieta = "Nie potrzebuję pośredników, poradzę sobie ze sprzedażą sam."
        nazwa_przycisku = "Sprzedam sam"

with r2_col1:
    if st.button("🚨 Zadzwonić później", use_container_width=True): 
        obiekcja_kliknieta = "Proszę zadzwonić za miesiąc, na razie dopiero wystawiłem."
        nazwa_przycisku = "Zadzwonić później"
with r2_col2:
    if st.button("🚨 Nie śpieszy mi się", use_container_width=True): 
        obiekcja_kliknieta = "Mnie się nie śpieszy ze sprzedażą, mogę poczekać na klienta."
        nazwa_przycisku = "Nie śpieszy mi się"
with r2_col3:
    if st.button("🚨 Nie zejdę z ceny", use_container_width=True): 
        obiekcja_kliknieta = "Chcę dostać dokładnie tyle ile w ogłoszeniu, zero negocjacji."
        nazwa_przycisku = "Nie zejdę z ceny"

# NOWE OBIEKCJE
with r3_col1:
    if st.button("🚨 Nie współpracuję z agencjami", use_container_width=True): 
        obiekcja_kliknieta = "Z zasady nie współpracuję z żadnymi pośrednikami i agencjami."
        nazwa_przycisku = "Nie współpracuję"
with r3_col2:
    if st.button("🚨 Przyprowadź klienta", use_container_width=True): 
        obiekcja_kliknieta = "Jak ma Pan klienta, to proszę przyprowadzić, ale umowy nie podpiszę."
        nazwa_przycisku = "Przyprowadź klienta"
with r3_col3:
    if st.button("🚨 Mam już kupca", use_container_width=True): 
        obiekcja_kliknieta = "Mam już zdecydowanego klienta, jutro daje zadatek."
        nazwa_przycisku = "Mam już kupca"

if obiekcja_kliknieta:
    client = pobierz_klienta_ai()
    if client:
        st.session_state.liczba_obiekcji += 1
        kontekst = st.session_state.analiza_nieruchomosci if st.session_state.analiza_nieruchomosci else "Brak danych o mieszkaniu."
        
        with st.spinner("AI analizuje sytuację..."):
            try:
                prompt_rozmowy = f"""Jesteś elitarnym coachem sprzedaży. 
                Strategia ogłoszenia: {kontekst}
                Klient mówi: '{obiekcja_kliknieta}'
                
                WYMOGI ODPOWIEDZI:
                1. ZWRACAJ SIĘ DO KLIENTA WYŁĄCZNIE W FORMIE GRZECZNOŚCIOWEJ: 'Pan', 'Pani' lub 'Państwo'. 
                2. Bezwzględnie unikaj mówienia do klienta na 'Ty'. Pełen profesjonalizm biznesowy.
                3. Musisz odpowiedzieć dokładnie w takim formacie:
                ODPOWIEDZ: [Tutaj wpisz profesjonalną, krótką na 2 zdania ripostę sprzedażową. Użyj argumentów z ogłoszenia.]
                SZANSA: [Tutaj wpisz tylko i wyłącznie jedną liczbę od 1 do 100, określającą szansę na spotkanie]"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_rozmowy}],
                    max_tokens=300
                )
                
                wynik = response.choices[0].message.content
                odpowiedz_tekst = wynik
                szansa_nowa = st.session_state.szansa_na_spotkanie
                
                if "ODPOWIEDZ:" in wynik and "SZANSA:" in wynik:
                    czesci = wynik.split("SZANSA:")
                    odpowiedz_tekst = czesci[0].replace("ODPOWIEDZ:", "").strip()
                    liczby = re.findall(r'\d+', czesci[1])
                    if liczby:
                        szansa_nowa = int(liczby[0])
                
                st.session_state.ostatnia_odpowiedz = odpowiedz_tekst
                st.session_state.szansa_na_spotkanie = szansa_nowa
                
                st.session_state.historia_rozmowy.append({
                    "klient": nazwa_przycisku,
                    "ai": odpowiedz_tekst,
                    "procent": szansa_nowa
                })
                st.rerun()
                
            except Exception as e:
                st.error(f"Błąd: {e}")

st.divider()

kol_lewa, kol_prawa = st.columns(2)

with kol_lewa:
    st.subheader("💡 Najnowsza wskazówka AI (Czytaj teraz):")
    st.info(st.session_state.ostatnia_odpowiedz)
    
    if st.session_state.szansa_na_spotkanie > 60:
        st.warning("🎯 PROPOZYCJA ZAMKNIĘCIA:\n*„Skoro tę kwestię mamy jasną, proponuję krótkie, 10-minutowe spotkanie na miejscu, abym mógł ocenić potencjał szybkiej transakcji. Środa 17:00 czy czwartek 11:00?”*")

with kol_prawa:
    st.subheader("📋 Oś czasu rozmowy (Twój raport):")
    if not st.session_state.historia_rozmowy:
        st.write("Rozmowa czysta. Brak historii.")
    else:
        for index, krok in enumerate(reversed(st.session_state.historia_rozmowy)):
            with st.chat_message("user"):
                st.write(f"**Klient rzucił obiekcję:** {krok['klient']} (Szansa: {krok['procent']}%)")
            with st.chat_message("assistant"):
                st.write(f"**AI podpowiedziało:** {krok['ai']}")
            st.text("---")
