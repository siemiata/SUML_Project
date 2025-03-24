import streamlit as st
import sqlite3
import random

def init_db():
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 pesel TEXT UNIQUE,
                 income REAL,
                 liabilities REAL)''')
    conn.commit()
    conn.close()

def add_customer(name, pesel, income, liabilities):
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO customers (name, pesel, income, liabilities) VALUES (?, ?, ?, ?)", 
                  (name, pesel, income, liabilities))
        conn.commit()
        st.success("Klient dodany pomyślnie!")
    except sqlite3.IntegrityError:
        st.error("Klient z tym numerem PESEL już istnieje!")
    conn.close()

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

def get_all_customers():
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    c.execute("SELECT * FROM customers")
    customers = c.fetchall()
    conn.close()
    return customers

def update_customer(pesel, new_name, new_income, new_liabilities):
    conn = sqlite3.connect("customers.db")
    c = conn.cursor()
    c.execute("UPDATE customers SET name = ?, income = ?, liabilities = ? WHERE pesel = ?", 
              (new_name, new_income, new_liabilities, pesel))
    conn.commit()
    conn.close()
    st.success("Dane klienta zostały zaktualizowane!")

def dummy_credit_score(): #losowe przyznawanie zdolności kredytowej
    return random.choice(["Good", "Standard", "Poor"])

st.set_page_config(page_title="Przewidywanie zdolności kredytowej", layout="centered")
st.title("Przewidywanie zdolności kredytowej")
init_db()

menu = st.sidebar.radio("Wybierz opcję", ["Dodaj klienta", "Szukaj klienta", "Edytuj klienta", "Wszyscy klienci"])

if menu == "Dodaj klienta":
    st.subheader("Dodawanie nowego klienta")
    with st.form("add_customer_form"):
        name = st.text_input("Imię i nazwisko")
        pesel = st.text_input("PESEL")
        income = st.number_input("Dochód", min_value=0.0, format="%.2f")
        liabilities = st.number_input("Zobowiązania", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Dodaj klienta")
        if submitted:
            if name and pesel and income >= 0 and liabilities >= 0:
                add_customer(name, pesel, income, liabilities)
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
            st.info(f"**Credit Score:** {dummy_credit_score()} (placeholder)")
        else:
            st.error("Nie znaleziono klienta.")

elif menu == "Edytuj klienta":
    st.subheader("Edycja danych klienta")
    with st.form("edit_customer_form"):
        edit_pesel = st.text_input("Podaj PESEL klienta do edycji")
        submitted = st.form_submit_button("Szukaj klienta")
    if submitted:
        customer = get_customer(pesel=edit_pesel)
        if customer:
            st.success("Klient znaleziony! Edytuj dane poniżej.")
            new_name = st.text_input("Nowe imię i nazwisko", value=customer[1])
            new_income = st.number_input("Nowy dochód", min_value=0.0, value=customer[3], format="%.2f")
            new_liabilities = st.number_input("Nowe zobowiązania", min_value=0.0, value=customer[4], format="%.2f")
            if st.button("Zapisz zmiany"):
                update_customer(edit_pesel, new_name, new_income, new_liabilities)
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
            st.info(f"**Credit Score:** {dummy_credit_score()} (placeholder)")
            st.write("---")
    else:
        st.error("Brak klientów w bazie.")