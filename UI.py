import streamlit as st
import pandas as pd
from datetime import date, timedelta

from models.user import User
from models.device import Device
from models.queries import Queries


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
# STARTSEITE
# -----------------------------------------------------------------------------

if choice == "Startseite":
    st.title("Admin-Dashboard Hochschule")
    st.info("Mockup der Geräte- & Nutzerverwaltung (Case Study I)")
    st.write("Navigation links verwenden.")

# -----------------------------------------------------------------------------
# GERÄTE-VERWALTUNG
# -----------------------------------------------------------------------------

elif choice == "Geräte-Verwaltung":

    users = User.find_all()
    user_emails = [u["email"] for u in users]
    user_lookup = {u["email"]: u["name"] for u in users}

    st.title("🛠️ Geräte-Verwaltung")

    tab1, tab2, tab3 = st.tabs(
        ["Geräteübersicht", "Neues Gerät anlegen", "Gerät bearbeiten"]
    )

    # -------------------------------
    # Geräteübersicht
    # -------------------------------
    with tab1:
        st.subheader("Inventarliste")

        devices = Device.find_all()

        if devices:
            devices_display = []
            for d in devices:
                d_copy = d.copy()
                email = d.get("responsible_person")
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

    # -------------------------------
    # Neues Gerät anlegen
    # -------------------------------
    with tab2:
        st.subheader("Gerät anlegen")

        if not users:
            st.warning("⚠️ Bitte zuerst einen Nutzer anlegen ⚠️")

        else:
            with st.form("add_device_form"):
                col1, col2 = st.columns(2)

                with col1:
                    new_name = st.text_input("Gerätename")
                    new_resp = st.selectbox("Verantwortliche Person", user_emails)
                    st.info("Inventar-ID wird automatisch vergeben")

                with col2:
                    new_cost = st.number_input("Wartungskosten (€)", min_value=0.0, step=10.0)
                    next_maintenance = st.date_input(
                        "Nächste Wartung",
                        value=date.today() + timedelta(days=180),
                        min_value=date.today()
                    )

                submitted = st.form_submit_button("Gerät speichern")

                if submitted:
                    if not new_name:
                        st.warning("Bitte Gerätenamen eingeben.")
                    else:
                        d = Device(
                            name=new_name,
                            managed_by_user_id=new_resp
                        )
                        # Zusatzfelder direkt anhängen
                        d.maintenance_cost = new_cost
                        d.next_maintenance = next_maintenance
                        d.store_data()

                        st.success("Gerät gespeichert.")
                        st.rerun()

    # -------------------------------
    # Gerät bearbeiten
    # -------------------------------
    with tab3:
        st.subheader("⚙️ Gerät bearbeiten")

        devices = Device.find_all()

        if not devices:
            st.info("Keine Geräte vorhanden.")
        else:
            device_map = {d["id"]: d for d in devices}

            selected_id = st.selectbox(
                "Gerät auswählen (Inventar-ID)",
                options=device_map.keys()
            )

            device = device_map[selected_id]

            if device["responsible_person"] in user_emails:
                selected_index = user_emails.index(device["responsible_person"])
            else:
                selected_index = 0

            with st.form("edit_device_form"):
                col1, col2 = st.columns(2)

                with col1:
                    edit_name = st.text_input("Gerätename", value=device["name"])
                    edit_resp = st.selectbox("Verantwortliche Person", user_emails, index=selected_index)

                with col2:
                    edit_cost = st.number_input("Wartungskosten (€)", value=float(device.get("maintenance_cost", 0.0)))
                    edit_next_maintenance = st.date_input(
                        "Nächste Wartung",
                        value=device.get("next_maintenance", date.today())
                    )

                save_clicked = st.form_submit_button("Änderungen speichern")

            if save_clicked:
                d = Device(
                    name=edit_name,
                    managed_by_user_id=edit_resp,
                    device_id=selected_id
                )
                d.maintenance_cost = edit_cost
                d.next_maintenance = edit_next_maintenance
                d.store_data()

                st.success("Gerät aktualisiert.")
                st.rerun()

            # -------------------------------
            # Löschen
            # -------------------------------
            st.markdown("---")
            st.warning(f"Gerät **{device['name']} ({selected_id})** wird gelöscht")

            delete_confirm = st.checkbox("Ich möchte dieses Gerät wirklich löschen")

            if delete_confirm:
                if st.button("🗑 Gerät endgültig löschen"):
                    Device("", "", device_id=selected_id).delete()
                    st.success("Gerät gelöscht.")
                    st.rerun()


# -----------------------------------------------------------------------------
# NUTZER-VERWALTUNG
# -----------------------------------------------------------------------------

elif choice == "Nutzer-Verwaltung":

    st.title("👥 Nutzer-Verwaltung")

    tab1, tab2, tab3 = st.tabs(
        ["Nutzerübersicht", "Nutzer anlegen", "Nutzer bearbeiten"]
    )

    # -------------------------------
    # Übersicht
    # -------------------------------
    with tab1:
        users = User.find_all()

        if users:
            df = pd.DataFrame(users)
            df = df.rename(columns={"name": "Name", "email": "E-Mail"})
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Keine Nutzer vorhanden.")

    # -------------------------------
    # Nutzer anlegen
    # -------------------------------
    with tab2:
        with st.form("add_user_form"):
            u_name = st.text_input("Name")
            u_email = st.text_input("E-Mail (ID)")
            submitted = st.form_submit_button("Nutzer speichern")

        if submitted:
            if not u_name or not u_email:
                st.error("Name und E-Mail dürfen nicht leer sein.")
            else:
                User(u_name, u_email).store_data()
                st.success("Nutzer gespeichert.")
                st.rerun()

    # -------------------------------
    # Nutzer bearbeiten
    # -------------------------------
    with tab3:
        users = User.find_all()

        if not users:
            st.info("Keine Nutzer vorhanden.")
        else:
            user_map = {u["email"]: u for u in users}

            selected_email = st.selectbox("Nutzer auswählen", options=user_map.keys())
            user = user_map[selected_email]

            with st.form("edit_user_form"):
                edit_name = st.text_input("Name", value=user["name"])
                save_clicked = st.form_submit_button("Änderungen speichern")

            if save_clicked:
                User(edit_name, selected_email).store_data()
                st.success("Nutzer aktualisiert.")
                st.rerun()

            # Löschen
            st.markdown("---")
            st.warning(f"Nutzer **{user['name']} ({selected_email})** wird gelöscht")

            delete_confirm = st.checkbox("Ich möchte diesen Nutzer wirklich löschen")

            if delete_confirm:
                if st.button("🗑 Nutzer endgültig löschen"):
                    User("", selected_email).delete()
                    st.success("Nutzer gelöscht.")
                    st.rerun()


# -----------------------------------------------------------------------------
# WARTUNGS-MANAGEMENT
# -----------------------------------------------------------------------------

elif choice == "Wartungs-Management":

    st.title("🔧 Wartungs-Management")

    devices = Device.find_all()

    total_cost = sum(d.get("maintenance_cost", 0) for d in devices)
    st.metric("Geschätzte Wartungskosten (Quartal)", f"{total_cost:.2f} €")

    st.subheader("Anstehende Wartungen")

    for d in devices:
        st.write(f"**{d['name']}** – nächste Wartung: {d.get('next_maintenance', 'n/a')}")
