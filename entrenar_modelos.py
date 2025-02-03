import os
import django

# Configuracion  entorno  Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_giss.settings') 
django.setup()

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from gestion_datos.models import Afiliado, CostosEstadisticas

# Función para entrenar el modelo de Regresión Logística
def entrenar_regresion_logistica():
    afiliados = Afiliado.objects.all().values()
    data = pd.DataFrame(afiliados)

    # Características de entrada
    X = data[['age', 'previous_consultations', 'previous_medication_cost']]
    y = (data['previous_hospitalizations'] > 0).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = LogisticRegression()
    modelo.fit(X_train, y_train)

    print("Modelo de Regresión Logística entrenado con éxito.")
    return modelo

# Función para entrenar el modelo Random Forest para consultas previas
def entrenar_random_forest_para_consultas():
    afiliados = Afiliado.objects.all().values()
    data = pd.DataFrame(afiliados)

    # Características de entrada
    X = data[['age', 'previous_hospitalizations', 'previous_medication_cost']]
    y = data['previous_consultations']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    print("Modelo Random Forest para consultas previas entrenado con éxito.")
    return modelo

# Función para entrenar el modelo Random Forest para costos de medicamentos
def entrenar_random_forest_para_costos():
    # Obtener los datos de los afiliados
    afiliados = Afiliado.objects.all().values()
    data = pd.DataFrame(afiliados)

    # Variables de entrada (características)
    X = data[['age', 'previous_hospitalizations', 'previous_consultations']]
    # Variable de salida (costo de medicamentos)
    y = data['previous_medication_cost']  # El costo de los medicamentos previos como objetivo

    # Dividir el conjunto de datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenar el modelo de Random Forest
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    print("Modelo Random Forest para costos de medicamentos entrenado con éxito.")
    return modelo

# Función para entrenar el modelo Random Forest para predicción de costos totales
def entrenar_random_forest_para_costos_totales():
    # Obtener los datos de los afiliados y costos
    afiliados = Afiliado.objects.all().values()
    costos_estadisticas = CostosEstadisticas.objects.all().values()

    # Convertir los datos a DataFrames
    df_afiliados = pd.DataFrame(afiliados)
    df_costos = pd.DataFrame(costos_estadisticas)

    # Aca se unen los datos de afiliados y costos usando el campo 'affiliate_id'
    df = pd.merge(df_afiliados, df_costos, on="affiliate_id")

    # Características de entrada (X)
    X = df[['age', 'previous_consultations', 'previous_hospitalizations', 'previous_medication_cost', 'risk_score', 'chronic_condition']]

    # Variable objetivo (y): Costo total de salud (medicación + procedimientos)
    y = df['total_medication_cost'] + df['total_procedure_cost']

    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crear y entrenar el modelo de Random Forest
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    print("Modelo Random Forest para costos totales entrenado con éxito.")
    return modelo


# Entrenar y guardar los modelos
if __name__ == '__main__':
    logistic_model = entrenar_regresion_logistica()
    joblib.dump(logistic_model, 'logistic_model.pkl')
    print("Modelo de Regresión Logística guardado como 'logistic_model.pkl'.")

    random_forest_model_consultas = entrenar_random_forest_para_consultas()
    joblib.dump(random_forest_model_consultas, 'random_forest_model_consultas.pkl')
    print("Modelo Random Forest para consultas previas guardado como 'random_forest_model_consultas.pkl'.")

    random_forest_model_costos = entrenar_random_forest_para_costos()
    joblib.dump(random_forest_model_costos, 'random_forest_model_costos.pkl')
    print("Modelo Random Forest para costos de medicamentos guardado como 'random_forest_model_costos.pkl'.")

    random_forest_model_costos_totales = entrenar_random_forest_para_costos_totales()
    joblib.dump(random_forest_model_costos_totales, 'random_forest_model_costos_totales.pkl')
    print("Modelo Random Forest para costos totales guardado como 'random_forest_model_costos_totales.pkl'.")
