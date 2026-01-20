import streamlit as st
import pandas as pd
from datetime import datetime,date, timedelta

# Services
from models.user_service import (
    get_users,
    add_user,
    update_user,
    delete_user,

)

from models.device_service import (
    get_devices,
    add_device,
    update_device,
    delete_device,
    unassign_devices_from_user
)



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

        if not users:
            st.warning("⚠️ Es existieren noch keine Nutzer ⚠️")
            st.info("Bitte zuerst einen Nutzer anlegen, bevor ein Gerät erstellt werden kann.")

        if users:
            with st.form("add_device_form"):
                col1, col2 = st.columns(2)

                with col1:
                    new_name = st.text_input("Gerätename")
                    new_resp = st.selectbox(
                        "Verantwortliche Person",
                        user_emails
                    )
                    st.info("Die Inventar-ID wird automatisch vergeben.")

                with col2:

                    new_cost = st.number_input(
                        "Wartungskosten (€)", min_value=0.0, step=10.0
                    )
                    next_maintenance = st.date_input(
                        "Nächste Wartung",
                        value=date.today() + timedelta(days=180),
                        min_value=date.today()
                    )

                submitted = st.form_submit_button("Gerät speichern")

                if submitted:
                    errors = []

                    if not new_name:
                        errors.append("Bitte Gerätenamen eingeben.")

                    if new_resp == "":
                        errors.append("Bitte eine verantwortliche Person auswählen.")

                    if errors:
                        for e in errors:
                            st.warning(e)
                    else:
                        add_device(
                            {
                                "name": new_name,
                                "responsible_person": new_resp,
                                "next_maintenance": next_maintenance.isoformat(),
                                "maintenance_cost": new_cost,
                            }
                        )
                        st.success("Gerät wurde gespeichert.")
                        st.rerun()

    # -------------------------------------------------------------------------
    # Gerät bearbeiten
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("⚙️ Gerät bearbeiten")

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

            # -------------------------------
            # defensiv: Index für Selectbox bestimmen
            # -------------------------------
            if device["responsible_person"] in user_emails:
                selected_index = user_emails.index(device["responsible_person"])
            else:
                selected_index = 0  # „nicht zugewiesen“

            # -------------------------------
            # FORM: Gerät bearbeiten
            # -------------------------------
            with st.form("edit_device_form"):
                col1, col2 = st.columns(2)

                with col1:
                    edit_name = st.text_input(
                        "Gerätename",
                        value=device["name"]
                    )
                    edit_resp = st.selectbox(
                        "Verantwortliche Person",
                        user_emails,
                        index=selected_index
                    )

                with col2:

                    edit_cost = st.number_input(
                        "Wartungskosten (€)",
                        min_value=0.0,
                        value=float(device["maintenance_cost"])
                    )
                    edit_next_maintenance = st.date_input(
                        "Nächste Wartung",
                        value=date.today() + timedelta(days=180),
                        min_value=date.today()
                    )

                save_clicked = st.form_submit_button("Änderungen speichern")

            # -------------------------------
            # Speichern
            # -------------------------------
            if save_clicked:
                if not edit_name:
                    st.error("Der Gerätename darf nicht leer sein.")
                else:
                    responsible_person = edit_resp if edit_resp in user_emails else None
                    update_device(
                        selected_id,
                        {
                            "id": selected_id,
                            "name": edit_name,
                            "responsible_person": responsible_person,
                            "next_maintenance": edit_next_maintenance.isoformat(),
                            "maintenance_cost": edit_cost,
                        }
                    )
                    st.success("Gerät wurde aktualisiert.")
                    st.rerun()

            # -------------------------------
            # LÖSCHEN
            # -------------------------------
            st.markdown("---")

            with st.container():
                st.markdown("### 🗑 Dieses Gerät löschen")

                st.warning(
                    f"Das Gerät **{device['name']} ({selected_id})** wird dauerhaft gelöscht "
                    "und kann nicht wiederhergestellt werden."
                )

                delete_confirm = st.checkbox(
                    "Ich möchte dieses Gerät wirklich löschen.",
                    key="delete_confirm"
                )

                col_spacer, col_button = st.columns([3, 1])

                with col_button:
                    if delete_confirm:
                        if st.button("🗑 Gerät endgültig löschen"):
                            success = delete_device(selected_id)

                            if success:
                                st.success("Gerät wurde gelöscht.")
                                st.rerun()
                            else:
                                st.error("Gerät konnte nicht gelöscht werden.")

# --- NUTZER-VERWALTUNG --------------------------------------------------------
elif choice == "Nutzer-Verwaltung":
    st.title("👥 Nutzer-Verwaltung")

    tab1, tab2, tab3 = st.tabs(
        ["Nutzerübersicht", "Nutzer anlegen", "Nutzer bearbeiten"]
    )

    # -------------------------------------------------------------------------
    # Nutzerübersicht
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("Registrierte Nutzer")

        users = get_users()

        if users:
            df = pd.DataFrame(users)
            df = df.rename(columns={
                "name": "Name",
                "email": "E-Mail"
            })
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Keine Nutzer vorhanden.")

    # -------------------------------------------------------------------------
    # Nutzer anlegen
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("Neuen Nutzer anlegen")

        with st.form("add_user_form"):
            u_name = st.text_input("Name")
            u_email = st.text_input("E-Mail (ID)")

            submitted = st.form_submit_button("Nutzer speichern")

        if submitted:
            if not u_name or not u_email:
                st.error("Name und E-Mail dürfen nicht leer sein.")
            else:
                add_user(
                    {
                        "name": u_name,
                        "email": u_email,
                    }
                )
                st.success("Nutzer wurde gespeichert.")
                st.rerun()

    # -------------------------------------------------------------------------
    # Nutzer bearbeiten
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("⚙️ Nutzer bearbeiten")

        users = get_users()

        if not users:
            st.info("Keine Nutzer vorhanden.")
        else:
            user_map = {u["email"]: u for u in users}

            selected_email = st.selectbox(
                "Nutzer auswählen (E-Mail)",
                options=user_map.keys()
            )

            user = user_map[selected_email]

            # -------------------------------
            # FORM: Nutzer bearbeiten
            # -------------------------------
            with st.form("edit_user_form"):
                edit_name = st.text_input(
                    "Name",
                    value=user["name"]
                )

                save_clicked = st.form_submit_button("Änderungen speichern")

            if save_clicked:
                if not edit_name:
                    st.error("Der Name darf nicht leer sein.")
                else:
                    update_user(
                        selected_email,
                        {
                            "email": selected_email,
                            "name": edit_name,
                        }
                    )
                    st.success("Nutzer wurde aktualisiert.")
                    st.rerun()

            # -------------------------------
            # Nutzer löschen
            # -------------------------------
            st.markdown("---")
            st.subheader("🗑️ Nutzer löschen")

            st.warning(
                f"Der Nutzer **{user['name']} ({selected_email})** wird dauerhaft gelöscht."
            )

            delete_confirm = st.checkbox(
                "Ich möchte diesen Nutzer wirklich löschen."
            )

            if delete_confirm:
                if st.button("🗑 Nutzer endgültig löschen"):
                    success = delete_user(selected_email)

                    if success:
                        st.success("Nutzer wurde gelöscht.")
                        st.rerun()
                    else:
                        st.error("Nutzer konnte nicht gelöscht werden.")

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
