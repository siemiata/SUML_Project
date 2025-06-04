from azure.storage.blob import BlobServiceClient
from datetime import datetime
import os
import sqlite3
import joblib
import streamlit as st

# Zapis danych do Azure Blob
def save_to_blob(input_text, output_text):
    try:
        folder = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        conn_str = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        container = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")

        blob_service = BlobServiceClient.from_connection_string(conn_str)
        container_client = blob_service.get_container_client(container)

        container_client.upload_blob(f"{folder}/input.txt", input_text)
        container_client.upload_blob(f"{folder}/output.txt", output_text)
    except Exception as e:
        st.error(f"❌ Błąd zapisu do Blob Storage: {e}")

# Model ML
model = joblib.load("model_decision_tree.pkl")

# Inicjalizacja bazy
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

# Dodawanie klienta
def add_customer(name, pesel, income, liabilities, age, employment_type, credit_history):
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO customers
            (name, pesel, income, liabilities, age, employment_type, credit_history)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, pesel, income, liabilities, age, employment_type, credit_history),
        )
        conn.commit()
        st.success("✅ Klient dodany!")
    except sqlite3.IntegrityError:
        st.error("❌ Klient z tym PESEL już istnieje!")
    conn.close()

# Pobranie jednego klienta
def get_customer(pesel=None, name=None):
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    if pesel and name:
        c.execute("SELECT * FROM customers WHERE pesel = ? OR name LIKE ?", (pesel, f"%{name}%"))
    elif pesel:
        c.execute("SELECT * FROM customers WHERE pesel = ?", (pesel,))
    elif name:
        c.execute("SELECT * FROM customers WHERE name LIKE ?", (f"%{name}%",))
    else:
        return None
    customer = c.fetchone()
    conn.close()
    return customer

# Pobranie wszystkich klientów
def get_all_customers():
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    customers = c.fetchall()
    conn.close()
    return customers

# Aktualizacja klienta
def update_customer(pesel, new_name, new_income, new_liabilities, new_age, new_employment_type, new_credit_history):
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    c.execute(
        """UPDATE customers SET
        name = ?, income = ?, liabilities = ?, age = ?,
        employment_type = ?, credit_history = ? WHERE pesel = ?""",
        (new_name, new_income, new_liabilities, new_age, new_employment_type, new_credit_history, pesel),
    )
    conn.commit()
    conn.close()
    st.success("✅ Dane zaktualizowane!")

# Predykcja
def credit_score_prediction(income, liabilities, age, employment_type, credit_history):
    employment_type_encoded = {"UoP": 0, "Zlecenie": 1, "B2B": 2}
    credit_history_encoded = {"Dobra": 0, "Średnia": 1, "Zła": 2, "Brak": 3}

    features = [[income, liabilities, age,
                employment_type_encoded[employment_type],
                credit_history_encoded[credit_history]]]
    prediction = model.predict(features)[0]
    return "Warto udzielić kredytu" if prediction == 1 else "Nie warto udzielać kredytu"

# Streamlit UI
st.set_page_config(page_title="Zdolność kredytowa", layout="centered")
st.title("📊 Przewidywanie zdolności kredytowej")
init_db()

menu = st.sidebar.radio("Wybierz opcję", ["Dodaj klienta", "Szukaj klienta", "Edytuj klienta", "Wszyscy klienci"])

if menu == "Dodaj klienta":
    st.subheader("Dodawanie nowego klienta")
    with st.form("add_customer_form"):
        name = st.text_input("Imię i nazwisko")
        pesel = st.text_input("PESEL")
        income = st.number_input("Dochód", min_value=0.0)
        liabilities = st.number_input("Zobowiązania", min_value=0.0)
        age = st.number_input("Wiek", min_value=18, max_value=120)
        employment_type = st.selectbox("Zatrudnienie", ["UoP", "Zlecenie", "B2B"])
        credit_history = st.selectbox("Historia kredytowa", ["Dobra", "Średnia", "Zła", "Brak"])
        submitted = st.form_submit_button("Dodaj klienta")
        if submitted and name and pesel:
            add_customer(name, pesel, income, liabilities, age, employment_type, credit_history)

elif menu == "Szukaj klienta":
    st.subheader("Wyszukiwanie klienta")
    with st.form("search_customer_form"):
        search_pesel = st.text_input("PESEL")
        search_name = st.text_input("Imię i nazwisko")
        submitted = st.form_submit_button("Szukaj")
    if submitted:
        customer = get_customer(search_pesel, search_name)
        if customer:
            st.success("✅ Klient znaleziony")
            st.write(f"**Imię i nazwisko:** {customer[1]}")
            st.write(f"**PESEL:** {customer[2]}")
            st.write(f"**Dochód:** {customer[3]:,.2f}")
            st.write(f"**Zobowiązania:** {customer[4]:,.2f}")
            st.write(f"**Wiek:** {customer[5]}")
            st.write(f"**Zatrudnienie:** {customer[6]}")
            st.write(f"**Historia kredytowa:** {customer[7]}")
            wynik = credit_score_prediction(customer[3], customer[4], customer[5], customer[6], customer[7])
            st.info(f"📈 Zdolność kredytowa: {wynik}")
            save_to_blob(f"{customer}", wynik)
        else:
            st.error("❌ Klient nie znaleziony.")

elif menu == "Edytuj klienta":
    st.subheader("Edycja danych klienta")
    with st.form("edit_customer_form"):
        pesel = st.text_input("PESEL klienta")
        search = st.form_submit_button("Szukaj")
    if search:
        customer = get_customer(pesel=pesel)
        if customer:
            with st.form("update_form"):
                new_name = st.text_input("Imię i nazwisko", value=customer[1])
                new_income = st.number_input("Dochód", value=customer[3])
                new_liabilities = st.number_input("Zobowiązania", value=customer[4])
                new_age = st.number_input("Wiek", min_value=18, max_value=120, value=customer[5])
                new_employment_type = st.selectbox("Zatrudnienie", ["UoP", "Zlecenie", "B2B"], index=["UoP", "Zlecenie", "B2B"].index(customer[6]))
                new_credit_history = st.selectbox("Historia kredytowa", ["Dobra", "Średnia", "Zła", "Brak"], index=["Dobra", "Średnia", "Zła", "Brak"].index(customer[7]))
                save = st.form_submit_button("Zapisz zmiany")
                if save:
                    update_customer(pesel, new_name, new_income, new_liabilities, new_age, new_employment_type, new_credit_history)
        else:
            st.error("❌ Klient nie znaleziony")

elif menu == "Wszyscy klienci":
    st.subheader("Lista wszystkich klientów")
    for c in get_all_customers():
        st.write(f"**{c[1]} ({c[2]})**")
        st.write(f"Dochód: {c[3]}, Zobowiązania: {c[4]}, Wiek: {c[5]}, Zatrudnienie: {c[6]}, Historia: {c[7]}")
        wynik = credit_score_prediction(c[3], c[4], c[5], c[6], c[7])
        st.info(f"📈 Zdolność kredytowa: {wynik}")
        st.write("---")


print()
print()
