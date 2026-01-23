import streamlit as st
import pandas as pd
from datetime import date
from models import Device, User 


# PAGE CONFIG
st.set_page_config(page_title="Geräte-Verwaltung Spiegl/Dörr", layout="wide")

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Menü:", ["Startseite", "Geräte-Verwaltung", "Nutzer-Verwaltung"])


# STARTSEITE
if choice == "Startseite":
    st.title("Admin-Dashboard Hochschule")
    st.info("Geräte- & Nutzerverwaltung (Case Study II)")


# GERÄTE-VERWALTUNG
elif choice == "Geräte-Verwaltung":
    
    # Daten laden über Klassenmethoden
    users = User.find_all()
    user_emails = ["— nicht zugewiesen —"] + [u.email for u in users]
    user_lookup = {u.email: u.name for u in users}

    st.title("🛠️ Geräte-Verwaltung")
    tab1, tab2, tab3 = st.tabs(["Übersicht", "Neu anlegen", "Bearbeiten"])

    # --- TAB 1: Übersicht ---
    with tab1:
        devices = Device.find_all() # Gibt Liste von Device-Objekten zurück
        if devices:
            # Für Pandas müssen wir die Objekte wieder in Dicts wandeln oder Attribute extrahieren
            data_for_df = []
            for d in devices:
                data_for_df.append({
                    "Inventar-ID": d.id,
                    "Gerätename": d.name,
                    "Verantwortlich": user_lookup.get(d.responsible_person, d.responsible_person),
                    "Wartung am": d.next_maintenance,
                    "Kosten": d.maintenance_cost
                })
            st.dataframe(pd.DataFrame(data_for_df), use_container_width=True)
        else:
            st.info("Keine Geräte vorhanden.")

    # --- TAB 2: Neu anlegen ---
    with tab2:
        with st.form("add_device"):
            name = st.text_input("Gerätename")
            resp = st.selectbox("Verantwortliche Person", user_emails)
            cost = st.number_input("Kosten", min_value=0.0, step=10.0)
            date_val = st.date_input("Nächste Wartung", value=date.today())
            
            if st.form_submit_button("Speichern"):
                responsible = None if resp == "— nicht zugewiesen —" else resp
                
                # Objekt erstellen und speichern
                new_device = Device(
                    name=name, 
                    responsible_person=responsible,
                    next_maintenance=date_val,
                    maintenance_cost=cost
                )
                new_device.store_data() # Speichert sich selbst
                
                st.success("Gerät gespeichert!")
                st.rerun()

    # --- TAB 3: Bearbeiten ---
    with tab3:
        devices = Device.find_all()
        if devices:
            # Dictionary bauen: ID -> Device Objekt
            device_map = {d.id: d for d in devices}
            sel_id = st.selectbox("Gerät wählen", list(device_map.keys()))
            
            # Das ausgewählte Objekt
            dev = device_map[sel_id]

            with st.form("edit_device"):
                # Index für Selectbox finden
                try:
                    idx = user_emails.index(dev.responsible_person)
                except ValueError:
                    idx = 0
                
                new_name = st.text_input("Name", value=dev.name)
                new_resp = st.selectbox("Verantwortlich", user_emails, index=idx)
                new_cost = st.number_input("Kosten", value=float(dev.maintenance_cost))
                new_date = st.date_input("Wartung", value=dev.next_maintenance)

                if st.form_submit_button("Update"):
                    # Attribute am Objekt ändern
                    dev.name = new_name
                    dev.responsible_person = None if new_resp == "— nicht zugewiesen —" else new_resp
                    dev.maintenance_cost = new_cost
                    dev.next_maintenance = new_date
                    
                    dev.store_data() # Update in DB
                    st.success("Aktualisiert!")
                    st.rerun()
            
            # Löschen
            if st.button("Löschen"):
                dev.delete()
                st.warning("Gelöscht!")
                st.rerun()


# NUTZER-VERWALTUNG
elif choice == "Nutzer-Verwaltung":
    st.title("👥 Nutzer-Verwaltung")
    
    with st.form("new_user"):
        u_name = st.text_input("Name")
        u_email = st.text_input("E-Mail")
        if st.form_submit_button("Nutzer anlegen"):
            if u_email:
                User(u_email, u_name).store_data()
                st.success("Angelegt")
                st.rerun()
    
    st.divider()
    
    users = User.find_all()
    if users:
        for u in users:
            col1, col2 = st.columns([4, 1])
            col1.write(f"**{u.name}** ({u.email})")
            
            # Eindeutiger Key für den Button ist wichtig!
            if col2.button("Löschen", key=f"del_{u.email}"):
                success = u.delete()
                
                if success:
                    st.success(f"Nutzer '{u.name}' wurde gelöscht.")
                    st.rerun()
                else:
                    st.error(f"Löschen nicht möglich: '{u.name}' ist noch für Geräte verantwortlich! Bitte weisen Sie die Geräte erst jemand anderem zu.")