import os
import django

# Configura el entorno de Django antes de cualquier otra cosa
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_giss.settings')  # Ajusta 'pro_giss' si tu proyecto tiene otro nombre
django.setup()

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from gestion_datos.models import Afiliado

# Función para entrenar el modelo de Regresión Logística
def entrenar_regresion_logistica():
    afiliados = Afiliado.objects.all().values()
    data = pd.DataFrame(afiliados)

    X = data[['age', 'previous_consultations', 'previous_medication_cost']]
    y = (data['previous_hospitalizations'] > 0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = LogisticRegression()
    modelo.fit(X_train, y_train)

    print("Modelo de Regresión Logística entrenado con éxito.")
    return modelo

# Función para entrenar el modelo Random Forest
def entrenar_random_forest():
    afiliados = Afiliado.objects.all().values()
    data = pd.DataFrame(afiliados)

    X = data[['age', 'previous_hospitalizations', 'previous_medication_cost']]
    y = data['previous_consultations']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    print("Modelo Random Forest entrenado con éxito.")
    return modelo

# Entrenar y guardar los modelos
if __name__ == '__main__':
    logistic_model = entrenar_regresion_logistica()
    joblib.dump(logistic_model, 'logistic_model.pkl')
    print("Modelo de Regresión Logística guardado como 'logistic_model.pkl'.")

    random_forest_model = entrenar_random_forest()
    joblib.dump(random_forest_model, 'random_forest_model.pkl')
    print("Modelo Random Forest guardado como 'random_forest_model.pkl'.")
