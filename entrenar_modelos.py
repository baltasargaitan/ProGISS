import os
import django
from sklearn.calibration import LabelEncoder

# Configuracion  entorno  Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_giss.settings') 
django.setup()

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from gestion_datos.models import Afiliado, CostosEstadisticas, EstudioProcedimiento

# Función para entrenar el modelo de Regresión Logística
def entrenar_regresion_logistica():
    afiliados = Afiliado.objects.all().values()
    data = pd.DataFrame(afiliados)

    # Crear la columna 'hospitalizacion_futura' como una estimación simple
    # Si el afiliado ha tenido hospitalizaciones en el pasado (columna 'previous_hospitalizations' > 0), asignamos 1 (hospitalización futura)
    data['hospitalizacion_futura'] = (data['previous_hospitalizations'] > 0).astype(int)

    # Características de entrada
    X = data[['age', 'previous_consultations', 'previous_medication_cost']]  # Características relevantes
    y = data['hospitalizacion_futura']  # El objetivo es predecir hospitalización futura

    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenar el modelo de Regresión Logística
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


def entrenar_random_forest_para_costos_totales():
    # Obtener los datos de los afiliados y costos
    afiliados = Afiliado.objects.all().values()
    costos_estadisticas = CostosEstadisticas.objects.all().values()

    # Convertir los datos a DataFrames
    df_afiliados = pd.DataFrame(afiliados)
    df_costos = pd.DataFrame(costos_estadisticas)

    # Asegurarse de que 'affiliate_id' sea del mismo tipo en ambos DataFrames
    df_afiliados['affiliate_id'] = df_afiliados['affiliate_id'].astype(str)
# Convertir los valores de 'affiliate_id' en df_costos al formato 'AF-<número>'
    df_costos['affiliate_id'] = df_costos['affiliate_id'].apply(lambda x: f"AF-{int(x):04d}")

    # Ahora puedes hacer la combinación sin problemas
    df = pd.merge(df_afiliados, df_costos, on="affiliate_id")

    print(f"Cantidad de registros después de la combinación: {len(df)}")

    print(df.isnull().sum())  # Para ver cuántos valores nulos hay

    # Eliminar filas con valores nulos en las columnas necesarias
    df = df.dropna(subset=['age', 'previous_consultations', 'previous_hospitalizations', 
                           'previous_medication_cost', 'risk_score', 'chronic_condition', 
                           'total_medication_cost', 'total_procedure_cost'])

    # Verificar si después de eliminar los nulos quedan suficientes datos para el entrenamiento
    print(f"Número de muestras para entrenamiento: {len(df)}")

    print("Valores de 'affiliate_id' en df_afiliados:", df_afiliados['affiliate_id'].unique())
    print("Valores de 'affiliate_id' en df_costos:", df_costos['affiliate_id'].unique())

    if len(df) > 0:
        # Características de entrada (X)
        X = df[['age', 'previous_consultations', 'previous_hospitalizations', 
                'previous_medication_cost', 'risk_score', 'chronic_condition']]

        # Variable objetivo (y): Costo total de salud (medicación + procedimientos)
        y = df['total_medication_cost'] + df['total_procedure_cost']

        # Dividir los datos en conjuntos de entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=42)

        # Crear y entrenar el modelo de Random Forest
        modelo = RandomForestRegressor(n_estimators=100, random_state=42)
        modelo.fit(X_train, y_train)

        # Guardar el modelo entrenado
        joblib.dump(modelo, 'random_forest_model_costos_totales.pkl')
        print("Modelo de Random Forest para costos totales guardado con éxito.")

    else:
        print("No hay suficientes datos para entrenar el modelo.")

def entrenar_random_forest_para_estudios():
    # Consultamos los datos de los estudios y afiliados
    estudios = EstudioProcedimiento.objects.all().values()
    afiliados = Afiliado.objects.all().values()

    # Convertimos a DataFrame
    df_estudios = pd.DataFrame(estudios)
    df_afiliados = pd.DataFrame(afiliados)

    # Verificamos las columnas de los DataFrames
    print(df_estudios.columns)

    # Asegúrate de que 'patient_id' y 'affiliate_id' tengan el mismo formato
    # Si 'patient_id' es numérico en los estudios y 'affiliate_id' es de tipo 'AF-XXXX' en los afiliados
    df_estudios['patient_id'] = df_estudios['patient_id'].apply(lambda x: f"AF-{str(x).zfill(4)}")

    # Ahora realizamos el merge usando las claves de tipo 'AF-XXXX'
    df = pd.merge(df_estudios, df_afiliados, left_on='patient_id', right_on='affiliate_id')

    # Verificamos el tamaño de la data después del merge
    print(f"Cantidad de registros después de la combinación: {df.shape[0]}")

    # Generar la variable objetivo (cantidad de estudios)
    df['cantidad_estudios'] = df.groupby('affiliate_id')['procedure_id'].transform('count')

    # Segmentar por edad
    df['grupo_edad'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 65, 100], labels=['0-18', '19-35', '36-50', '51-65', '66+'])

    # Convertir las variables categóricas
    label_encoder = LabelEncoder()
    df['plan'] = label_encoder.fit_transform(df['plan'])
    df['grupo_edad'] = label_encoder.fit_transform(df['grupo_edad'])

    # Características de entrada (X)
    X = df[['age', 'plan', 'grupo_edad']]  # Incluye variables de edad y plan
    # Variable objetivo (y): cantidad de estudios
    y = df['cantidad_estudios']

    # Dividir los datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crear y entrenar el modelo Random Forest
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    print("Modelo Random Forest para predicción de cantidad de estudios entrenado con éxito.")
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

    modelo_estudios = entrenar_random_forest_para_estudios()
    joblib.dump(modelo_estudios, 'random_forest_model_estudios.pkl')
    print("Modelo Random Forest para cantidad de estudios guardado como 'random_forest_model_estudios.pkl'.")
