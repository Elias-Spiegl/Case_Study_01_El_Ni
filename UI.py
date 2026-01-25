import streamlit as st
import pandas as pd
from datetime import date, timedelta

from models.user import User
from models.device import Device
from models.queries import UserQueries, DeviceQueries


# -----------------------------------------------------------------------------
# PAGE CONFIG & NAVIGATION
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Geräte-Verwaltung – Case Study II",
    layout="wide"
)

st.sidebar.title("Navigation")
choice = st.sidebar.radio(
    "Menü wählen:",
    [
        "Startseite",
        "Geräte-Verwaltung",
        "Nutzer-Verwaltung",
        "Wartungs-Management",
    ],
)

# -----------------------------------------------------------------------------
# STARTSEITE
# -----------------------------------------------------------------------------

if choice == "Startseite":
    st.title("Admin-Dashboard Hochschule")
    st.info("Geräte- & Nutzerverwaltung – Case Study II")
    st.write("Navigation links verwenden.")


# -----------------------------------------------------------------------------
# GERÄTE-VERWALTUNG
# -----------------------------------------------------------------------------

elif choice == "Geräte-Verwaltung":

    users = UserQueries.find_all()
    devices = DeviceQueries.find_all()

    user_ids = [u.id for u in users]
    user_lookup = {u.id: u.name for u in users}

    st.title("🛠️ Geräte-Verwaltung")

    tab1, tab2, tab3 = st.tabs(
        ["Geräteübersicht", "Neues Gerät anlegen", "Gerät bearbeiten"]
    )

    # -------------------------------
    # Geräteübersicht
    # -------------------------------
    with tab1:
        st.subheader("Inventarliste")

        if devices:
            rows = []
            for d in devices:
                rows.append({
                    "Inventar-ID": d.id,
                    "Gerätename": d.device_name,
                    "Verantwortliche Person": user_lookup.get(d.managed_by_user_id, d.managed_by_user_id),
                    "Nächste Wartung": getattr(d, "next_maintenance", None),
                    "Wartungskosten (€)": getattr(d, "maintenance_cost", 0.0)
                })

            st.dataframe(pd.DataFrame(rows), width="stretch")
        else:
            st.info("Keine Geräte vorhanden.")

    # -------------------------------
    # Neues Gerät anlegen
    # -------------------------------
    with tab2:
        st.subheader("Gerät anlegen")

        if not users:
            st.warning("Bitte zuerst einen Nutzer anlegen.")
        else:
            with st.form("add_device_form"):
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Gerätename")
                    responsible = st.selectbox("Verantwortliche Person", user_ids)

                with col2:
                    cost = st.number_input("Wartungskosten (€)", min_value=0.0, step=10.0)
                    next_maintenance = st.date_input(
                        "Nächste Wartung",
                        value=date.today() + timedelta(days=180),
                        min_value=date.today()
                    )

                submit = st.form_submit_button("Gerät speichern")

            if submit:
                if not name:
                    st.warning("Bitte Gerätenamen eingeben.")
                else:
                    d = Device(name=name, managed_by_user_id=responsible)
                    d.maintenance_cost = cost
                    d.next_maintenance = next_maintenance
                    DeviceQueries.save(d)

                    st.success("Gerät gespeichert.")
                    st.rerun()

    # -------------------------------
    # Gerät bearbeiten
    # -------------------------------
    with tab3:
        st.subheader("⚙️ Gerät bearbeiten")

        if not devices:
            st.info("Keine Geräte vorhanden.")
        else:
            device_map = {d.id: d for d in devices}
            selected_id = st.selectbox("Gerät auswählen", device_map.keys())
            device = device_map[selected_id]

            with st.form("edit_device_form"):
                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Gerätename", value=device.device_name)
                    responsible = st.selectbox(
                        "Verantwortliche Person",
                        user_ids,
                        index=user_ids.index(device.managed_by_user_id)
                    )

                with col2:
                    cost = st.number_input(
                        "Wartungskosten (€)",
                        value=float(getattr(device, "maintenance_cost", 0.0))
                    )
                    next_maintenance = st.date_input(
                        "Nächste Wartung",
                        value=getattr(device, "next_maintenance", date.today())
                    )

                save = st.form_submit_button("Änderungen speichern")

            if save:
                device.device_name = name
                device.managed_by_user_id = responsible
                device.maintenance_cost = cost
                device.next_maintenance = next_maintenance

                DeviceQueries.save(device)
                st.success("Gerät aktualisiert.")
                st.rerun()

            st.markdown("---")
            st.warning(f"Gerät **{device.device_name} ({device.id})** wird gelöscht")

            if st.checkbox("Ich möchte dieses Gerät wirklich löschen"):
                if st.button("🗑 Gerät endgültig löschen"):
                    DeviceQueries.delete(device.id)
                    st.success("Gerät gelöscht.")
                    st.rerun()


# -----------------------------------------------------------------------------
# NUTZER-VERWALTUNG
# -----------------------------------------------------------------------------

elif choice == "Nutzer-Verwaltung":

    st.title("👥 Nutzer-Verwaltung")

    users = UserQueries.find_all()

    tab1, tab2, tab3 = st.tabs(
        ["Nutzerübersicht", "Nutzer anlegen", "Nutzer bearbeiten"]
    )

    # -------------------------------
    # Übersicht
    # -------------------------------
    with tab1:
        if users:
            st.dataframe(
                pd.DataFrame(
                    [{"Name": u.name, "E-Mail": u.id} for u in users]
                ),
                width="stretch"
            )
        else:
            st.info("Keine Nutzer vorhanden.")

    # -------------------------------
    # Nutzer anlegen
    # -------------------------------
    with tab2:
        with st.form("add_user_form"):
            name = st.text_input("Name")
            email = st.text_input("E-Mail (ID)")
            submit = st.form_submit_button("Nutzer speichern")

        if submit:
            if not name or not email:
                st.error("Name und E-Mail dürfen nicht leer sein.")
            else:
                UserQueries.save(User(name, email))
                st.success("Nutzer gespeichert.")
                st.rerun()

    # -------------------------------
    # Nutzer bearbeiten
    # -------------------------------
    with tab3:
        if not users:
            st.info("Keine Nutzer vorhanden.")
        else:
            user_map = {u.id: u for u in users}
            selected_id = st.selectbox("Nutzer auswählen", user_map.keys())
            user = user_map[selected_id]

            with st.form("edit_user_form"):
                name = st.text_input("Name", value=user.name)
                save = st.form_submit_button("Änderungen speichern")

            if save:
                user.name = name
                UserQueries.save(user)
                st.success("Nutzer aktualisiert.")
                st.rerun()

            st.markdown("---")
            st.warning(f"Nutzer **{user.name} ({user.id})** wird gelöscht")

            if st.checkbox("Ich möchte diesen Nutzer wirklich löschen"):
                if st.button("🗑 Nutzer endgültig löschen"):
                    UserQueries.delete(user.id)
                    st.success("Nutzer gelöscht.")
                    st.rerun()


# -----------------------------------------------------------------------------
# WARTUNGS-MANAGEMENT
# -----------------------------------------------------------------------------

elif choice == "Wartungs-Management":

    st.title("🔧 Wartungs-Management")

    devices = DeviceQueries.find_all()

    total_cost = sum(getattr(d, "maintenance_cost", 0) for d in devices)
    st.metric("Geschätzte Wartungskosten (Quartal)", f"{total_cost:.2f} €")

    for d in devices:
        st.write(f"**{d.device_name}** – nächste Wartung: {getattr(d, 'next_maintenance', 'n/a')}")
