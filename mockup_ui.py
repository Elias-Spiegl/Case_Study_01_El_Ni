import streamlit as st
import pandas as pd
from datetime import datetime

# Services
from services.device_service import get_devices, add_device , update_device
from services.user_service import get_users, add_user

# -----------------------------------------------------------------------------
# PAGE CONFIG & NAVIGATION
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Geräte-Verwaltung – Case Study I",
    layout="wide"
)

st.sidebar.title("Navigation")
choice = st.sidebar.radio(
    "Menü wählen:",
    [
        "Startseite",
        "Geräte-Verwaltung",
        "Nutzer-Verwaltung",
        "Reservierungssystem",
        "Wartungs-Management",
    ],
)

# -----------------------------------------------------------------------------
# 3. UI
# -----------------------------------------------------------------------------

# --- STARTSEITE ---------------------------------------------------------------
if choice == "Startseite":
    st.title("Admin-Dashboard Hochschule")
    st.info("Mockup der Geräte- & Nutzerverwaltung (Case Study I)")
    st.write("Navigation links verwenden.")

# --- GERÄTE-VERWALTUNG --------------------------------------------------------
elif choice == "Geräte-Verwaltung":
    users = get_users()
    user_emails = [u["email"] for u in users]

    # Lookup: Mail → Name (für Anzeige)
    user_lookup = {u["email"]: u["name"] for u in users}

    st.title("🛠️ Geräte-Verwaltung")

    tab1, tab2, tab3 = st.tabs(
        ["Geräteübersicht", "Neues Gerät anlegen", "Gerät bearbeiten"]
    )

    # -------------------------------------------------------------------------
    # Geräteübersicht
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("Inventarliste")

        devices = get_devices()
        if devices:
            # Anzeige-Daten aufbereiten (nur für UI!)
            devices_display = []
            for d in devices:
                d_copy = d.copy()
                email = d["responsible_person"]
                d_copy["responsible_person"] = user_lookup.get(email, email)
                devices_display.append(d_copy)

            df = pd.DataFrame(devices_display)
            df = df.rename(columns={
                "id": "Inventar-ID",
                "name": "Gerätename",
                "responsible_person": "Verantwortliche Person",
                "next_maintenance": "Nächste Wartung",
                "maintenance_cost": "Wartungskosten (€)"
            })

            st.dataframe(df, use_container_width=True)
        else:
            st.info("Keine Geräte vorhanden.")

    # -------------------------------------------------------------------------
    # Neues Gerät anlegen
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("Gerät anlegen")

        with st.form("add_device_form"):
            col1, col2 = st.columns(2)

            with col1:
                new_id = st.text_input("Inventarnummer (ID)")
                new_name = st.text_input("Gerätename")

            with col2:
                new_resp = st.selectbox(
                    "Verantwortliche Person",
                    user_emails
                )
                new_cost = st.number_input(
                    "Wartungskosten (€)", min_value=0.0, step=10.0
                )

            submitted = st.form_submit_button("Gerät speichern")

            if submitted:
                add_device(
                    {
                        "id": new_id,
                        "name": new_name,
                        "responsible_person": new_resp,
                        "next_maintenance": str(datetime.now().date()),
                        "maintenance_cost": new_cost,
                    }
                )
                st.success("Gerät wurde gespeichert.")
                st.rerun()

    # -------------------------------------------------------------------------
    # Gerät bearbeiten
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("Gerät bearbeiten")

        devices = get_devices()

        if not devices:
            st.info("Keine Geräte vorhanden.")
        else:
            device_map = {d["id"]: d for d in devices}

            selected_id = st.selectbox(
                "Gerät auswählen (Inventar-ID)",
                options=device_map.keys()
            )

            device = device_map[selected_id]

            with st.form("edit_device_form"):
                col1, col2 = st.columns(2)

                with col1:
                    edit_name = st.text_input(
                        "Gerätename", value=device["name"]
                    )

                with col2:
                    edit_resp = st.selectbox(
                        "Verantwortliche Person",
                        user_emails,
                        index=user_emails.index(device["responsible_person"])
                    )
                    edit_cost = st.number_input(
                        "Wartungskosten (€)",
                        min_value=0.0,
                        value=float(device["maintenance_cost"])
                    )

                submitted = st.form_submit_button("Änderungen speichern")

                if submitted:
                    update_device(
                        selected_id,
                        {
                            "id": selected_id,
                            "name": edit_name,
                            "responsible_person": edit_resp,
                            "next_maintenance": device["next_maintenance"],
                            "maintenance_cost": edit_cost,
                        }
                    )
                    st.success("Gerät wurde aktualisiert.")
                    st.rerun()

# --- NUTZER-VERWALTUNG --------------------------------------------------------
elif choice == "Nutzer-Verwaltung":
    st.title("👥 Nutzer-Verwaltung")

    tab1, tab2 = st.tabs(["Nutzerübersicht", "Nutzer anlegen"])

    # --- Nutzerübersicht ---
    with tab1:
        st.subheader("Registrierte Nutzer")

        users = get_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True)
        else:
            st.info("Keine Nutzer vorhanden.")

    # --- Nutzer anlegen ---
    with tab2:
        st.subheader("Neuen Nutzer anlegen")

        with st.form("add_user_form"):
            u_name = st.text_input("Name")
            u_email = st.text_input("E-Mail (ID)")

            submitted = st.form_submit_button("Nutzer speichern")

            if submitted:
                add_user(
                    {
                        "name": u_name,
                        "email": u_email,
                    }
                )
                st.success("Nutzer wurde gespeichert.")
                st.rerun()


# --- WARTUNGS-MANAGEMENT ------------------------------------------------------
elif choice == "Wartungs-Management":
    st.title("🔧 Wartungs-Management")

    devices = get_devices()

    total_cost = sum(d["maintenance_cost"] for d in devices)
    st.metric("Geschätzte Wartungskosten (Quartal)", f"{total_cost:.2f} €")

    st.subheader("Anstehende Wartungen")
    for d in devices:
        st.write(
            f"**{d['name']}** – nächste Wartung: {d.get('next_maintenance', 'n/a')}"
        )
