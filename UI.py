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
            st.info ("Löschen des Nutzers")

            delete_confirm = st.checkbox("Ich möchte diesen Nutzer wirklich löschen")

            if delete_confirm:

                device_count = Device.count_by_user(selected_email)

                if device_count > 0:
                    st.error(
                        f"Dieser Nutzer verwaltet noch {device_count} Gerät(e). "
                        "Bitte zuerst Geräte neu zuweisen oder löschen."
                    )
                else:
                    User("", selected_email).delete()
                    st.success("Nutzer gelöscht.")
                    st.rerun()


# -----------------------------------------------------------------------------
# RESERVIERUNGSSYSTEM
# -----------------------------------------------------------------------------

elif choice == "Reservierungssystem":

    from models.reservation import Reservation

    st.title("📅 Reservierungssystem")

    users = User.find_all()
    devices = Device.find_all()

    if not users or not devices:
        st.info("Bitte zuerst Nutzer und Geräte anlegen.")
        st.stop()

    # ------------------------
    # Lookups bauen
    # ------------------------

    user_emails = [u["email"] for u in users]
    user_lookup = {u["email"]: u["name"] for u in users}

    device_lookup = {d["id"]: d["name"] for d in devices}

    # Label → ID Map für Geräte-Dropdown
    device_label_map = {
        f'{d["name"]} ({d["id"]})': d["id"]
        for d in devices
    }
    device_labels = list(device_label_map.keys())

    # ------------------------
    # Tabs
    # ------------------------

    tab1, tab2, tab3 = st.tabs(
        ["Reservierungs Übersicht", "Neue Reservierung", "Reservierung bearbeiten"]
    )

    # =========================================================
    # TAB 1 — Übersicht
    # =========================================================

    with tab1:

        reservations = Reservation.find_all()

        if reservations:
            display = []

            for r in reservations:
                r_copy = r.copy()
                r_copy["device"] = f'{device_lookup.get(r["device_id"], r["device_id"])} ({r["device_id"]})'
                r_copy["user"] = user_lookup.get(r["user_email"], r["user_email"])
                display.append(r_copy)

            df = pd.DataFrame(display)[["id", "device", "user", "start_date", "end_date"]]
            df = df.rename(columns={
                "id": "Reservierungs-ID",
                "device": "Gerät",
                "user": "Nutzer",
                "start_date": "Startdatum",
                "end_date": "Enddatum"
            })

            st.dataframe(df, use_container_width=True)

        else:
            st.info("Keine Reservierungen vorhanden.")

    # =========================================================
    # TAB 2 — Neue Reservierung
    # =========================================================

    with tab2:

        with st.form("add_reservation"):

            sel_user = st.selectbox("Nutzer", user_emails)

            sel_device_label = st.selectbox("Gerät", device_labels)
            sel_device = device_label_map[sel_device_label]

            start = st.date_input("Startdatum", date.today())
            end = st.date_input("Enddatum", date.today() + timedelta(days=1))

            submitted = st.form_submit_button("Reservieren")

        if submitted:
            if end < start:
                st.error("Enddatum muss nach Startdatum liegen.")
            elif not Reservation.is_device_available(sel_device, start, end):
                st.error("❌ Gerät ist in diesem Zeitraum bereits reserviert.")
            else:
                Reservation(sel_device, sel_user, start, end).store_data()
                st.success("✅ Reservierung gespeichert")
                st.rerun()

    # =========================================================
    # TAB 3 — Bearbeiten / Löschen
    # =========================================================

    with tab3:

        reservations = Reservation.find_all()

        if not reservations:
            st.info("Keine Reservierungen vorhanden.")
            st.stop()

        res_map = {r["id"]: r for r in reservations}

        selected_res_id = st.selectbox("Reservierung auswählen", res_map.keys())
        res = res_map[selected_res_id]

        # Aktuelles Geräte-Label finden
        current_device_label = next(
            label for label, did in device_label_map.items()
            if did == res["device_id"]
        )

        with st.form("edit_res_form"):

            edit_device_label = st.selectbox(
                "Gerät",
                device_labels,
                index=device_labels.index(current_device_label)
            )
            edit_device = device_label_map[edit_device_label]

            edit_user = st.selectbox(
                "Nutzer",
                user_emails,
                index=user_emails.index(res["user_email"])
            )

            edit_start = st.date_input("Startdatum", res["start_date"])
            edit_end = st.date_input("Enddatum", res["end_date"])

            save = st.form_submit_button("Änderungen speichern")

        # -------- speichern --------
        if save:
            if edit_end < edit_start:
                st.error("Enddatum muss nach Startdatum liegen.")
            elif not Reservation.is_device_available(
                edit_device, edit_start, edit_end, ignore_res_id=selected_res_id
            ):
                st.error("❌ Gerät ist in diesem Zeitraum bereits reserviert.")
            else:
                Reservation(
                    edit_device,
                    edit_user,
                    edit_start,
                    edit_end,
                    reservation_id=selected_res_id
                ).store_data()

                st.success("Reservierung aktualisiert.")
                st.rerun()

        # -------- löschen --------
        st.markdown("---")
        st.subheader("🗑 Reservierung löschen")

        del_confirm = st.checkbox("Ich möchte diese Reservierung wirklich löschen")

        if del_confirm:
            if st.button("Reservierung endgültig löschen"):
                Reservation(None, None, None, None, reservation_id=selected_res_id).delete()
                st.success("Reservierung gelöscht.")
                st.rerun()

# -----------------------------------------------------------------------------
# WARTUNGS-MANAGEMENT
# -----------------------------------------------------------------------------

elif choice == "Wartungs-Management":

    st.title("🔧 Wartungs-Management")

    devices = Device.find_all()
    users = User.find_all()

    if not devices:
        st.info("Keine Geräte vorhanden.")
        st.stop()

    # Lookup für Usernamen
    user_lookup = {u["email"]: u["name"] for u in users}

    today = date.today()

    display = []
    total_cost = 0.0
    due_soon_count = 0
    overdue_count = 0

    for d in devices:
        d_copy = d.copy()

        # Verantwortliche Person schöner anzeigen
        email = d.get("responsible_person")
        d_copy["responsible_person"] = user_lookup.get(email, email)

        # --- Wartungsdaten sicher holen ---
        next_maint = d.get("next_maintenance", None)
        cost = d.get("maintenance_cost", 0.0)

        # Falls keine Wartung gesetzt → Defaultwerte
        if next_maint is None:
            next_maint_display = "n/a"
            status = "n/a"
        else:
            next_maint_display = next_maint

            # Status bestimmen
            if next_maint < today:
                status = "🔴 Überfällig"
                overdue_count += 1
            elif next_maint <= today + timedelta(days=30):
                status = "🟠 Bald fällig"
                due_soon_count += 1
            else:
                status = "🟢 OK"

        # Werte sauber in Kopie setzen
        d_copy["next_maintenance"] = next_maint_display
        d_copy["maintenance_cost"] = cost
        d_copy["status"] = status

        total_cost += cost
        display.append(d_copy)

    # -------------------------------
    # Kennzahlen oben
    # -------------------------------

    col1, col2, col3 = st.columns(3)
    col1.metric("Gesamte Wartungskosten", f"{total_cost:.2f} €")
    col2.metric("Bald fällige Wartungen", due_soon_count)
    col3.metric("Überfällige Wartungen", overdue_count)

    st.markdown("---")

    # -------------------------------
    # Tabelle
    # -------------------------------

    df = pd.DataFrame(display)

    df = df.rename(columns={
        "id": "Inventar-ID",
        "name": "Gerätename",
        "responsible_person": "Verantwortliche Person",
        "next_maintenance": "Nächste Wartung",
        "maintenance_cost": "Wartungskosten (€)",
        "status": "Status"
    })

    df = df[
        [
            "Inventar-ID",
            "Gerätename",
            "Verantwortliche Person",
            "Nächste Wartung",
            "Wartungskosten (€)",
            "Status"
        ]
    ]

    st.dataframe(df, use_container_width=True)
