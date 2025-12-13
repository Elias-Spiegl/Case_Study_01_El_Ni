import streamlit as st

# Seitentitel
st.set_page_config(page_title="Geräte-Verwaltung Case Study I")
st.title("Geräte-Verwaltung Hochschule")

# Navigation (Struktur der App nachbauen laut Bild)
menu = ["Startseite", "Geräte-Verwaltung", "Nutzer-Verwaltung", "Reservierungssystem", "Wartungs-Management"]
choice = st.sidebar.selectbox("Menü", menu)

# Begrüßung auf der Startseite
if choice == "Startseite":
    st.subheader("Willkommen im Admin-Dashboard")
    st.write("Wählen Sie einen Bereich aus dem Menü links.")

# Initialisierung von Platzhalter-Daten im Session State (wie im Bild gefordert)
if 'devices' not in st.session_state:
    # Feste Platzhalter-Werte basierend auf den Attributen aus PDF 04_02 [cite: 138, 139]
    st.session_state.devices = [
        {"id": "INV-001", "name": "3D-Drucker Prusa", "responsible": "Elias Mustermann"},
        {"id": "INV-002", "name": "Laser Cutter", "responsible": "Nico Mustermann"},
    ]

if 'users' not in st.session_state:
    # Platzhalter für Nutzer (Attribute: id/email, name) [cite: 114, 115]
    st.session_state.users = [
        {"email": "max@hs.edu", "name": "Max Mustermann"},
        {"email": "erika@hs.edu", "name": "Erika Musterfrau"}
    ]


    # UI für Geräte-Verwaltung
if choice == "Geräte-Verwaltung":
    st.subheader("Geräte verwalten")

    # 1. Bestehende Geräte anzeigen (liest aus unserem Platzhalter-State)
    st.write("### Aktuelle Geräteliste")
    st.table(st.session_state.devices)
    
    st.divider()

    # 2. Mockup für "Gerät anlegen" [cite: 91]
    st.write("### Neues Gerät anlegen")
    
    # Input-Felder basierend auf den Attributen im PDF 
    col1, col2 = st.columns(2)
    with col1:
        new_id = st.text_input("Inventarnummer (ID)")
        new_name = st.text_input("Gerätename")
    with col2:
        # Hier nutzen wir die Nutzer-Platzhalter für die Dropdown-Liste
        user_list = [u['name'] for u in st.session_state.users]
        responsible = st.selectbox("Verantwortliche Person", user_list)
        maintenance_cost = st.number_input("Wartungskosten (€)", min_value=0.0, step=10.0)

    # Button ohne komplexe Logik (nur UI-Struktur)
    if st.button("Gerät speichern"):
        st.success(f"Gerät '{new_name}' wurde (simuliert) gespeichert!")
        # Optional: Hier könnte man später die Liste in st.session_state.devices erweitern