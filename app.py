import streamlit as st
from groq import Groq
import re

# Konfiguracja okna aplikacji
st.set_page_config(page_title="AI Sales Coach - Agency Standard", layout="wide", initial_sidebar_state="expanded")

# BEZPIECZEŃSTWO: Pobieranie klucza z ukrytego sejfu
KLUCZ_API = st.secrets["GROQ_API_KEY"]

# --- PAMIĘĆ APLIKACJI (SESSION STATE) ---
if "analiza_nieruchomosci" not in st.session_state:
    st.session_state.analiza_nieruchomosci = None
if "pytania_spin" not in st.session_state:
    st.session_state.pytania_spin = "Wklej ogłoszenie po lewej stronie, aby wygenerować pytania badające."
if "szansa_na_spotkanie" not in st.session_state:
    st.session_state.szansa_na_spotkanie = 10
if "liczba_obiekcji" not in st.session_state:
    st.session_state.liczba_obiekcji = 0
if "ostatnia_odpowiedz" not in st.session_state:
    st.session_state.ostatnia_odpowiedz = "Czekam na pierwszą obiekcję..."
if "historia_rozmowy" not in st.session_state:
    st.session_state.historia_rozmowy = [] 
# NOWOŚĆ: Szufladka na wygenerowanego SMS-a
if "wygenerowany_sms" not in st.session_state:
    st.session_state.wygenerowany_sms = None

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
            with st.spinner("Analiza w toku..."):
                try:
                    prompt_analizy = f"""Przeanalizuj to ogłoszenie: '{opis}'
                    Wyciągnij: 1. Główne atuty 2. Słabe punkty (pole do negocjacji)."""
                    
                    response_analiza = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt_analizy}],
                        max_tokens=400
                    )
                    st.session_state.analiza_nieruchomosci = response_analiza.choices[0].message.content
                    
                    prompt_spin = f"""Jesteś doradcą ds. nieruchomości dzwoniącym do WŁAŚCICIELA, który wystawił to mieszkanie na sprzedaż: '{opis}'.
                    Zbuduj 3 otwarte, nienachalne pytania (technika SPIN), które zadasz SPRZEDAJĄCEMU na początku rozmowy (cold call), aby zbadać jego motywację, czas na rynku i ewentualne trudności ze sprzedażą.
                    Kategoryczny zakaz zadawania pytań z perspektywy kupującego.
                    Zwracaj się do właściciela per 'Pan/Pani/Państwo'."""

                    response_spin = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt_spin}],
                        max_tokens=400
                    )
                    st.session_state.pytania_spin = response_spin.choices[0].message.content
                    
                    # Resetowanie statystyk przed nową rozmową
                    st.session_state.szansa_na_spotkanie = 15
                    st.session_state.liczba_obiekcji = 0
                    st.session_state.historia_rozmowy = []
                    st.session_state.wygenerowany_sms = None
                except Exception as e:
                    st.error(f"Błąd analizy: {e}")

    if st.session_state.analiza_nieruchomosci:
        st.success("Strategia gotowa.")
        
    # --- STOPKA AUTORSKA ---
    st.markdown("<br><br><br>", unsafe_allow_html=True) 
    st.markdown("<div style='text-align: center; color: gray; font-size: 12px;'>Designed and deployed by Paweł 🚀</div>", unsafe_allow_html=True)

# --- GŁÓWNY EKRAN ---
st.title("🎙️ Cold Calls - Make it SIMPLE as f*ck")

m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="Szansa na spotkanie", value=f"{st.session_state.szansa_na_spotkanie}%")
with m2:
    st.metric(label="Przepracowane obiekcje", value=st.session_state.liczba_obiekcji)
with m3:
    st.metric(label="Status relacji", value="Wysokie zaangażowanie" if st.session_state.szansa_na_spotkanie > 50 else "Badanie potrzeb")

st.divider()

st.subheader("🟡 Koło Ratunkowe: Pytania do zadania na początku")
st.warning(st.session_state.pytania_spin)

st.divider()

# SIATKA OBIEKCJI
st.subheader("🔥 Właściciel rzuca obiekcję:")
r1_col1, r1_col2, r1_col3 = st.columns(3)
r2_col1, r2_col2, r2_col3 = st.columns(3)
r3_col1, r3_col2, r3_col3 = st.columns(3)

obiekcja_kliknieta = None
nazwa_przycisku = ""

with r1_col1:
    if st.button("🚨 Sprzedam sam", use_container_width=True): 
        obiekcja_kliknieta = "Nie potrzebuję pośredników, poradzę sobie ze sprzedażą sam."
        nazwa_przycisku = "Sprzedam sam"
with r1_col2:
    if st.button("🚨 Nie płacę prowizji", use_container_width=True): 
        obiekcja_kliknieta = "Nie chcę płacić prowizji, to za duży koszt."
        nazwa_przycisku = "Nie płacę prowizji"
with r1_col3:
    if st.button("🚨 Mam już pośrednika", use_container_width=True): 
        obiekcja_kliknieta = "Mam już podpisaną umowę z innym pośrednikiem."
        nazwa_przycisku = "Mam już pośrednika"

with r2_col1:
    if st.button("🚨 Zapraszam z klientem", use_container_width=True): 
        obiekcja_kliknieta = "Jak ma Pan klienta, to proszę przyjść, ale bez umowy."
        nazwa_przycisku = "Zapraszam z klientem"
with r2_col2:
    if st.button("🚨 Pośrednicy nic nie robią", use_container_width=True): 
        obiekcja_kliknieta = "Pośrednicy nic nie robią, tylko wrzucają ogłoszenie na portal."
        nazwa_przycisku = "Pośrednicy nic nie robią"
with r2_col3:
    if st.button("🚨 Nie podpisuję umów", use_container_width=True): 
        obiekcja_kliknieta = "Nie chcę wiązać się żadnymi umowami na wyłączność."
        nazwa_przycisku = "Nie podpisuję umów"

with r3_col1:
    if st.button("🚨 Mam już kupca", use_container_width=True): 
        obiekcja_kliknieta = "Mam już kogoś chętnego, jutro dajemy zadatek."
        nazwa_przycisku = "Mam już kupca"
with r3_col2:
    if st.button("🚨 Nie wpuszczam obcych", use_container_width=True): 
        obiekcja_kliknieta = "Nie chcę wpuszczać obcych ludzi do mieszkania żeby tylko oglądali."
        nazwa_przycisku = "Nie wpuszczam obcych"
with r3_col3:
    if st.button("🚨 Nie mam czasu", use_container_width=True): 
        obiekcja_kliknieta = "Nie mam teraz czasu na spotkania i rozmowy o sprzedaży."
        nazwa_przycisku = "Nie mam czasu"

if obiekcja_kliknieta:
    client = pobierz_klienta_ai()
    if client:
        st.session_state.liczba_obiekcji += 1
        kontekst = st.session_state.analiza_nieruchomosci if st.session_state.analiza_nieruchomosci else "Brak danych."
        
        with st.spinner("AI generuje ripostę zgodnie ze standardami agencji..."):
            try:
                prompt_rozmowy = f"""Jesteś doradcą ds. nieruchomości. Twoim celem jest zaciekawić, zbudować zaufanie i umówić spotkanie.
                Nie sprzedajesz umowy ani prowizji - sprzedajesz spokój, bezpieczeństwo i skuteczność.
                Strategia ogłoszenia: {kontekst}
                Klient mówi: '{obiekcja_kliknieta}'
                
                ZASADY ODPOWIEDZI (BEZWZGLĘDNE):
                1. Mów na 'Pan/Pani/Państwo'. Nigdy na 'Ty'.
                2. SCHEMAT: Najpierw przyjmij obiekcję (np. 'Rozumiem'), potem zadaj pytanie pogłębiające, a dopiero potem krótko użyj języka korzyści. Rozmowa to konsultacja, a nie walka.
                3. BAZA WIEDZY DO WYKORZYSTANIA (użyj odpowiedniej w zależności od obiekcji):
                   - Sprzedam sam: Zapytaj jak długo sprzedają. Wielu zaczyna samemu, naszą rolą jest skrócenie procesu i bezpieczeństwo.
                   - Prowizja: Pytaj, czy gdyby sprzedano drożej/szybciej to byłby problem. Koszt to źle przeprowadzona sprzedaż, nie prowizja.
                   - Mam pośrednika: Nie krytykuj! Zapytaj czy wyłączność czy otwarta, czy są zadowoleni z liczby prezentacji. 
                   - Z klientem: Zapytaj co jeśli ten jeden nie kupi? Nie uzależniamy sprzedaży od jednego klienta.
                   - Brak czasu: Dlatego dzwonię. Przejmujemy pracę.
                   - Nie wpuszczam obcych: My weryfikujemy klientów przed prezentacją.
                   - Umowa: Nie naciskaj na umowę. Proponujesz spotkanie.
                
                WYMOGI FORMATU:
                ODPOWIEDZ: [Krótka, naturalna riposta zgodna z Zasadami]
                SZANSA: [Liczba od 1 do 100 określająca % szansy na spotkanie]"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_rozmowy}],
                    max_tokens=350
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
                st.session_state.wygenerowany_sms = None # Reset SMSa przy nowej obiekcji
                st.rerun()
                
            except Exception as e:
                st.error(f"Błąd: {e}")

st.divider()

kol_lewa, kol_prawa = st.columns(2)

with kol_lewa:
    st.subheader("💡 Odpowiedź AI (Standard Firmowy):")
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
                st.write(f"**Klient:** {krok['klient']} (Szansa: {krok['procent']}%)")
            with st.chat_message("assistant"):
                st.write(f"**Ty:** {krok['ai']}")
            st.text("---")

st.divider()

# --- MODUŁ FEEDBACKU I ZAMKNIĘCIA ROZMOWY ---
st.subheader("📊 Zamknięcie i Follow-up")
col_sukces, col_porazka = st.columns(2)

with col_sukces:
    if st.button("✅ UDAŁO SIĘ (Mamy spotkanie!)", use_container_width=True):
        client = pobierz_klienta_ai()
        if client:
            with st.spinner("Generowanie profesjonalnego SMS-a dla klienta..."):
                try:
                    przebieg = "\n".join([f"Klient: {k['klient']}" for k in st.session_state.historia_rozmowy])
                    prompt_sms = f"""Jesteś elitarnym doradcą ds. nieruchomości (imię: Paweł, agencja: Simple).
                    Właśnie zakończyłeś rozmowę z właścicielem mieszkania (cold call) i udało Ci się umówić na spotkanie, by ocenić potencjał nieruchomości.
                    Przebieg rozmowy (obiekcje klienta): {przebieg}
                    
                    ZADANIE:
                    Napisz krótkiego (max 3 zdania), ultra-profesjonalnego SMS-a z podziękowaniem za rozmowę.
                    Użyj wstawki '[DATA I GODZINA]', w której Paweł ręcznie wpisze termin. 
                    Nawiąż jednym zdaniem do obaw klienta z przebiegu rozmowy (np. jeśli klient mówił o prowizji, napisz, że pokażesz mu jak zoptymalizować zysk; jeśli mówił 'Sprzedam sam', napisz że pokażesz jak możemy przyspieszyć ten proces).
                    Podpisz się na końcu: 'Paweł, agencja Simple'. 
                    Bez powitań w stylu 'Oto twój SMS'. Zwróć od razu samą treść SMS-a."""
                    
                    response_sms = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt_sms}],
                        max_tokens=200
                    )
                    st.session_state.wygenerowany_sms = response_sms.choices[0].message.content
                except Exception as e:
                    st.error(f"Błąd generowania SMS: {e}")

with col_porazka:
    if st.button("❌ NIE TYM RAZEM (Odmowa)", use_container_width=True):
        st.info("Zapisano. System wyciągnie wnioski na podstawie osi czasu do przyszłych statystyk.")

# Wyświetlanie wygenerowanego SMS-a pod przyciskami
if st.session_state.wygenerowany_sms:
    st.success("🎉 Świetna robota! Skopiuj ten tekst i wyślij klientowi ze swojego telefonu:")
    st.code(st.session_state.wygenerowany_sms, language="text")
