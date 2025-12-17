import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. SESSION STATE INITIALISIERUNG ("Fake-Daten")
# -----------------------------------------------------------------------------

# Alle zu speichernden Variablen werden in diesem Abschnitt initialisiert
# Sie werden alleridnsg nicht in einer Datenbank gespeichert sonder
# im Session_state abgelegt (Temporärer speicher in streamlit)
# vergleichbar mit einem py Dictionary...


# Initialisiere Nutzer-Daten (Attribute laut PDF 04_02, Seite 7)
if 'users' not in st.session_state:
    st.session_state.users = [
        {"email": "max.mustermann@hs.edu", "name": "Max Mustermann"},
        {"email": "julia.student@hs.edu", "name": "Julia Student"},
    ]

# Initialisiere Geräte-Daten

if 'devices' not in st.session_state:
    st.session_state.devices = [
        {
            "id": "INV-001", 
            "name": "3D-Drucker Prusa MK3", 
            "responsible_person": "max.mustermann@hs.edu",
            "next_maintenance": "2024-01-15",
            "maintenance_cost": 50.0
        },
        {
            "id": "INV-002", 
            "name": "Laser Cutter Epilog", 
            "responsible_person": "max.mustermann@hs.edu",
            "next_maintenance": "2024-02-01",
            "maintenance_cost": 120.0
        },
    ]

# -----------------------------------------------------------------------------
# 2. SEITEN-KONFIGURATION & NAVIGATION
# Strukturierung der 4 Use-Cases in einer Seitenleiste
# -----------------------------------------------------------------------------

st.set_page_config(page_title="Geräte-Verwaltung Case Study I", layout="wide")

st.sidebar.title("Navigation")
menu_options = [
    "Startseite", 
    "Geräte-Verwaltung", 
    "Nutzer-Verwaltung", 
    "Reservierungssystem", 
    "Wartungs-Management"
]
choice = st.sidebar.radio("Menü wählen:", menu_options)

# -----------------------------------------------------------------------------
# 3. IMPLEMENTIERUNG DES UI-MOCKUPS
# -----------------------------------------------------------------------------

# --- STARTSEITE ---
if choice == "Startseite":
    st.title("Admin-Dashboard Hochschule")
    st.info("Willkommen im Mockup der Geräte-Verwaltung.")
    st.write("Wählen Sie links einen Bereich aus, um die UI zu testen.")

# --- GERÄTE-VERWALTUNG ---
elif choice == "Geräte-Verwaltung":
    st.title("🛠️ Geräte-Verwaltung")
    
    tab1, tab2 = st.tabs(["Geräteübersicht", "Neues Gerät anlegen"])
    
    with tab1:
        st.subheader("Aktuelle Inventarliste")
        # Umwandlung in DataFrame für schönere Darstellung
        if st.session_state.devices:
            df_devices = pd.DataFrame(st.session_state.devices)
            st.dataframe(df_devices, use_container_width=True)
        else:
            st.write("Keine Geräte vorhanden.")

    with tab2:
        st.subheader("Gerät hinzufügen (Mockup)")
        with st.form("new_device_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("Inventarnummer (ID)")
                new_name = st.text_input("Gerätename")
            with col2:
                # Dropdown basierend auf den Nutzern im Session State
                user_options = [u['email'] for u in st.session_state.users]
                new_resp = st.selectbox("Verantwortliche Person", user_options)
                new_cost = st.number_input("Wartungskosten (€)", min_value=0.0)
            
            submitted = st.form_submit_button("Gerät speichern")
            
            if submitted:
                # Hier simulieren wir das Speichern (nur im Session State)
                new_device = {
                    "id": new_id,
                    "name": new_name,
                    "responsible_person": new_resp,
                    "next_maintenance": str(datetime.now().date()), # Dummy Datum
                    "maintenance_cost": new_cost
                }
                st.session_state.devices.append(new_device)
                st.success(f"Gerät '{new_name}' wurde simuliert gespeichert!")
                st.rerun() # Lädt die Seite neu, damit die Tabelle aktualisiert wird (
                           # Session_Stat ebelibt natürlich erhalten)

# --- NUTZER-VERWALTUNG ---
elif choice == "Nutzer-Verwaltung":
    st.title("👥 Nutzer-Verwaltung")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Registrierte Nutzer")
        st.table(st.session_state.users)
        
    with col2:
        st.subheader("Nutzer anlegen")
        with st.form("user_form"):
            u_name = st.text_input("Name")
            u_email = st.text_input("E-Mail (ID)")
            
            if st.form_submit_button("Nutzer anlegen"):
                st.session_state.users.append({"email": u_email, "name": u_name})
                st.success("Nutzer hinzugefügt!")
                st.rerun()

# --- RESERVIERUNGSSYSTEM ---
elif choice == "Reservierungssystem":

    st.title("📅 Reservierungssystem")
    st.warning("Hinweis: Dies ist nur ein UI-Entwurf.")
    
    # Auswahl der Objekte aus den Platzhalter-Daten
    device_names = [d['name'] for d in st.session_state.devices]
    user_names = [u['name'] for u in st.session_state.users]

    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("Gerät wählen", device_names)
        st.date_input("Startdatum")
    with c2:
        st.selectbox("Nutzer wählen", user_names)
        st.date_input("Enddatum")
        
    st.button("Reservierung prüfen & buchen")

# --- WARTUNGS-MANAGEMENT ---
elif choice == "Wartungs-Management":

    st.title("🔧 Wartungs-Management")
    
    # Einfache Berechnung basierend auf den Platzhalter-Daten
    total_cost = sum(d['maintenance_cost'] for d in st.session_state.devices) # Wartungskosten aufsummieren
    
    st.metric(label="Geschätzte Wartungskosten (Quartal)", value=f"{total_cost} €")
    
    st.subheader("Anstehende Wartungen")
    # Zeige nur Geräte an, die wir im State haben
    for dev in st.session_state.devices:
        st.write(f"**{dev['name']}**: Nächste Wartung am {dev.get('next_maintenance', 'Unbekannt')}")