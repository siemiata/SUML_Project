# Przewidywanie zdolności kredytowej

Projekt ten ma na celu stworzenie modelu uczenia maszynowego do klasyfikacji zdolności kredytowej ("credit score") na podstawie danych finansowych. Wykorzystując odpowiednie techniki analizy danych oraz algorytmy ML, model będzie przewidywał ocenę kredytową klientów na podstawie dostępnych informacji.

## Funkcjonalności

Aplikacja posiada następujące funkcje:

- **Dodawanie nowego klienta:** Umożliwia dodanie klienta do bazy danych, z podstawowymi danymi, takimi jak imię, nazwisko, PESEL, dochód i zobowiązania.
- **Wyszukiwanie klienta:** Pozwala na wyszukiwanie klienta po numerze PESEL lub imieniu/nazwisku.
- **Edycja danych klienta:** Umożliwia edytowanie danych już istniejącego klienta w bazie danych.
- **Lista wszystkich klientów:** Wyświetla pełną listę klientów w bazie danych, pokazując ich dane oraz  wynik oceny kredytowej.

## Technologie

- **Python:** Język programowania używany do stworzenia aplikacji.
- **Streamlit:** Biblioteka do tworzenia aplikacji webowych w Pythonie, użyta do stworzenia interfejsu użytkownika.
- **SQLite:** Baza danych wykorzystywana do przechowywania danych klientów.

## Instalacja

Aby uruchomić aplikację należy:
- Zainstalować zależności: pip install -r requirements.txt
- Uruchomić aplikację poprzez CreditScoreApp.bat
