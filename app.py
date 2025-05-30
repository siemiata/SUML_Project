import sqlite3

import joblib
import streamlit as st

model = joblib.load("model_decision_tree.pkl")


def init_db():
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            pesel TEXT UNIQUE,
            income REAL,
            liabilities REAL,
            age INTEGER,
            employment_type TEXT,
            credit_history TEXT)"""
    )
    conn.commit()
    conn.close()


def add_customer(
    name, pesel, income, liabilities, age, employment_type, credit_history
):
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO customers
            (name, pesel, income, liabilities, age, employment_type,
             credit_history)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, pesel, income, liabilities, age, employment_type, credit_history),
        )
        conn.commit()
        st.success("Klient dodany pomyślnie!")
    except sqlite3.IntegrityError:
        st.error("Klient z tym numerem PESEL już istnieje!")
    conn.close()


def get_customer(pesel=None, name=None):
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    if pesel and name:
        c.execute(
            "SELECT * FROM customers WHERE pesel = ? OR name LIKE ?",
            (pesel, f"%{name}%"),
        )
    elif pesel:
        c.execute("SELECT * FROM customers WHERE pesel = ?", (pesel,))
    elif name:
        c.execute("SELECT * FROM customers WHERE name LIKE ?", (f"%{name}%",))
    else:
        return None
    customer = c.fetchone()
    conn.close()
    return customer


def get_all_customers():
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    customers = c.fetchall()
    conn.close()
    return customers


def update_customer(
    pesel,
    new_name,
    new_income,
    new_liabilities,
    new_age,
    new_employment_type,
    new_credit_history,
):
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    c.execute(
        """UPDATE customers SET
        name = ?, income = ?, liabilities = ?, age = ?,
        employment_type = ?, credit_history = ? WHERE pesel = ?""",
        (
            new_name,
            new_income,
            new_liabilities,
            new_age,
            new_employment_type,
            new_credit_history,
            pesel,
        ),
    )
    conn.commit()
    conn.close()
    st.success("Dane klienta zostały zaktualizowane!")


def credit_score_prediction(income, liabilities, age, employment_type, credit_history):
    employment_type_encoded = {"UoP": 0, "Zlecenie": 1, "B2B": 2}
    credit_history_encoded = {"Dobra": 0, "Średnia": 1, "Zła": 2, "Brak": 3}

    features = [
        [
            income,
            liabilities,
            age,
            employment_type_encoded[employment_type],
            credit_history_encoded[credit_history],
        ]
    ]
    prediction = model.predict(features)[0]
    if prediction == 1:
        return "Warto udzielić kredytu"
    return "Nie warto udzielać kredytu"


st.set_page_config(page_title="Przewidywanie zdolności kredytowej", layout="centered")
st.title("Przewidywanie zdolności kredytowej")
init_db()

menu = st.sidebar.radio(
    "Wybierz opcję",
    ["Dodaj klienta", "Szukaj klienta", "Edytuj klienta", "Wszyscy klienci"],
)

if menu == "Dodaj klienta":
    st.subheader("Dodawanie nowego klienta")
    with st.form("add_customer_form"):
        name = st.text_input("Imię i nazwisko")
        pesel = st.text_input("PESEL")
        income = st.number_input("Dochód", min_value=0.0, format="%.2f")
        liabilities = st.number_input("Zobowiązania", min_value=0.0, format="%.2f")
        age = st.number_input("Wiek", min_value=18, max_value=120)
        employment_type = st.selectbox(
            "Rodzaj zatrudnienia", ["UoP", "Zlecenie", "B2B"]
        )
        credit_history = st.selectbox(
            "Historia kredytowa", ["Dobra", "Średnia", "Zła", "Brak"]
        )
        submitted = st.form_submit_button("Dodaj klienta")
        if submitted:
            if name and pesel:
                add_customer(
                    name,
                    pesel,
                    income,
                    liabilities,
                    age,
                    employment_type,
                    credit_history,
                )
            else:
                st.error("Wypełnij poprawnie wszystkie pola!")

elif menu == "Szukaj klienta":
    st.subheader("Wyszukiwanie klienta")
    with st.form("search_customer_form"):
        search_pesel = st.text_input("Podaj PESEL klienta")
        search_name = st.text_input("Podaj imię i nazwisko klienta")
        submitted = st.form_submit_button("Szukaj")
    if submitted:
        customer = get_customer(search_pesel, search_name)
        if customer:
            st.success("Klient znaleziony!")
            st.write(f"**Imię i nazwisko:** {customer[1]}")
            st.write(f"**PESEL:** {customer[2]}")
            st.write(f"**Dochód:** {customer[3]:,.2f} PLN")
            st.write(f"**Zobowiązania:** {customer[4]:,.2f} PLN")
            st.write(f"**Wiek:** {customer[5]}")
            st.write(f"**Zatrudnienie:** {customer[6]}")
            st.write(f"**Historia kredytowa:** {customer[7]}")
            credit_score = credit_score_prediction(
                customer[3], customer[4], customer[5], customer[6], customer[7]
            )
            st.info(f"**Zdolność kredytowa:** {credit_score}")
        else:
            st.error("Nie znaleziono klienta.")

elif menu == "Edytuj klienta":
    st.subheader("Edycja danych klienta")

    if "edit_pesel" not in st.session_state:
        st.session_state.edit_pesel = ""

    with st.form("edit_customer_form"):
        edit_pesel = st.text_input(
            "Podaj PESEL klienta do edycji", value=st.session_state.edit_pesel
        )
        submitted = st.form_submit_button("Szukaj klienta")
        if submitted:
            st.session_state.edit_pesel = edit_pesel

    if st.session_state.edit_pesel:
        customer = get_customer(pesel=st.session_state.edit_pesel)
        if customer:
            st.success("Klient znaleziony! Edytuj dane poniżej.")
            with st.form("update_customer_form"):
                new_name = st.text_input("Nowe imię i nazwisko", value=customer[1])
                new_income = st.number_input(
                    "Nowy dochód", min_value=0.0, value=customer[3], format="%.2f"
                )
                new_liabilities = st.number_input(
                    "Nowe zobowiązania", min_value=0.0, value=customer[4], format="%.2f"
                )
                new_age = st.number_input(
                    "Nowy wiek", min_value=18, max_value=120, value=customer[5]
                )
                new_employment_type = st.selectbox(
                    "Nowy rodzaj zatrudnienia",
                    ["UoP", "Zlecenie", "B2B"],
                    index=["UoP", "Zlecenie", "B2B"].index(customer[6]),
                )
                new_credit_history = st.selectbox(
                    "Nowa historia kredytowa",
                    ["Dobra", "Średnia", "Zła", "Brak"],
                    index=["Dobra", "Średnia", "Zła", "Brak"].index(customer[7]),
                )
                save_submitted = st.form_submit_button("Zapisz zmiany")
                if save_submitted:
                    update_customer(
                        st.session_state.edit_pesel,
                        new_name,
                        new_income,
                        new_liabilities,
                        new_age,
                        new_employment_type,
                        new_credit_history,
                    )
        else:
            st.error("Nie znaleziono klienta o podanym numerze PESEL.")

elif menu == "Wszyscy klienci":
    st.subheader("Lista wszystkich klientów")
    customers = get_all_customers()
    if customers:
        for customer in customers:
            st.write(f"**Imię i nazwisko:** {customer[1]}")
            st.write(f"**PESEL:** {customer[2]}")
            st.write(f"**Dochód:** {customer[3]:,.2f} PLN")
            st.write(f"**Zobowiązania:** {customer[4]:,.2f} PLN")
            st.write(f"**Wiek:** {customer[5]}")
            st.write(f"**Zatrudnienie:** {customer[6]}")
            st.write(f"**Historia kredytowa:** {customer[7]}")
            credit_score = credit_score_prediction(
                customer[3], customer[4], customer[5], customer[6], customer[7]
            )
            st.info(f"**Zdolność kredytowa:** {credit_score}")
            st.write("---")
    else:
        st.error("Brak klientów w bazie.")

