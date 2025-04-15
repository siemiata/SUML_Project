import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv('dane.csv')

label_encoder = LabelEncoder()

df['employment_type'] = label_encoder.fit_transform(df['employment_type'])
df['credit_history'] = label_encoder.fit_transform(df['credit_history'])

X = df[['income', 'liabilities', 'age', 'employment_type', 'credit_history']]
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier()

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f'Dokładność modelu: {accuracy:.2f}')

joblib.dump(model, 'model_decision_tree.pkl')
print("Model zapisany do pliku 'model_decision_tree.pkl'")
