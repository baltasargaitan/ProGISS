import os
import django


# Configuración del entorno Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_giss.settings') 
django.setup()
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.utils import resample
from sklearn.preprocessing import LabelEncoder
from gestion_datos.models import Afiliado, CostosEstadisticas, EstudioProcedimiento

# Función para entrenar el modelo de Regresión Logística para predecir hospitalización futura
def entrenar_regresion_logistica():
    """
    Esta función entrena un modelo de Regresión Logística para predecir la hospitalización futura de un afiliado.
    Utiliza las características de edad, consultas previas y costo de medicamentos previos, y genera la columna 
    'hospitalizacion_futura' para entrenar el modelo.
    """
    # Obtener los datos de los afiliados
    afiliados = Afiliado.objects.all().values()
    data = pd.DataFrame(afiliados)

    # Crear la columna 'hospitalizacion_futura' como una estimación simple
    data['hospitalizacion_futura'] = (data['previous_hospitalizations'] > 0).astype(int)

    # Verificar la distribución de 'hospitalizacion_futura'
    if data['hospitalizacion_futura'].nunique() < 2:
        print("Error: Los datos no tienen suficientes clases para entrenar el modelo.")
        return None

    # Eliminar filas con valores nulos
    data = data.dropna(subset=['age', 'previous_consultations', 'previous_medication_cost'])

    # Características de entrada
    X = data[['age', 'previous_consultations', 'previous_medication_cost']]
    y = data['hospitalizacion_futura']

    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Si hay desbalance en las clases, realizar oversampling en la clase minoritaria
    if y_train.value_counts().min() == 0:
        minority_class = X_train[y_train == 0]
        majority_class = X_train[y_train == 1]
        
        minority_class_upsampled = resample(minority_class, replace=True, n_samples=len(majority_class), random_state=42)
        X_train = pd.concat([majority_class, minority_class_upsampled])
        y_train = pd.concat([y_train[majority_class.index], y_train[minority_class_upsampled.index]])

    # Entrenar el modelo de Regresión Logística
    modelo = LogisticRegression(max_iter=1000)
    modelo.fit(X_train, y_train)

    print("Modelo de Regresión Logística entrenado con éxito.")
    return modelo

# Función para entrenar el modelo Random Forest para consultas previas
def entrenar_random_forest_para_consultas():
    """
    Esta función entrena un modelo de Random Forest para predecir las consultas previas realizadas por los afiliados,
    utilizando características como la edad, hospitalizaciones previas y costos de medicamentos previos.
    """
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
    """
    Esta función entrena un modelo de Random Forest para predecir los costos de medicamentos de los afiliados, 
    utilizando las características de edad, hospitalizaciones previas y consultas previas.
    """
    afiliados = Afiliado.objects.all().values()
    data = pd.DataFrame(afiliados)

    # Características de entrada
    X = data[['age', 'previous_hospitalizations', 'previous_consultations']]
    y = data['previous_medication_cost']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    print("Modelo Random Forest para costos de medicamentos entrenado con éxito.")
    return modelo

# Función para entrenar el modelo Random Forest para costos totales
def entrenar_random_forest_para_costos_totales():
    """
    Esta función entrena un modelo de Random Forest para predecir los costos totales de salud, que incluyen 
    medicamentos y procedimientos, basándose en las características de los afiliados y sus costos asociados.
    """
    afiliados = Afiliado.objects.all().values()
    costos_estadisticas = CostosEstadisticas.objects.all().values()

    # Convertir los datos a DataFrames
    df_afiliados = pd.DataFrame(afiliados)
    df_costos = pd.DataFrame(costos_estadisticas)

    # Asegurarse de que 'affiliate_id' sea del mismo tipo en ambos DataFrames
    df_afiliados['affiliate_id'] = df_afiliados['affiliate_id'].astype(str)
    df_costos['affiliate_id'] = df_costos['affiliate_id'].apply(lambda x: f"AF-{int(x):04d}")

    # Realizar el merge
    df = pd.merge(df_afiliados, df_costos, on="affiliate_id")

    # Eliminar filas con valores nulos
    df = df.dropna(subset=['age', 'previous_consultations', 'previous_hospitalizations', 
                           'previous_medication_cost', 'risk_score', 'chronic_condition', 
                           'total_medication_cost', 'total_procedure_cost'])

    # Verificar si después de eliminar los nulos quedan suficientes datos para el entrenamiento
    if len(df) > 0:
        # Características de entrada (X)
        X = df[['age', 'previous_consultations', 'previous_hospitalizations', 
                'previous_medication_cost', 'risk_score', 'chronic_condition']]

        # Variable objetivo (y): Costo total de salud
        y = df['total_medication_cost'] + df['total_procedure_cost']

        # Dividir los datos en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=42)

        # Crear y entrenar el modelo de Random Forest
        modelo = RandomForestRegressor(n_estimators=100, random_state=42)
        modelo.fit(X_train, y_train)

        # Guardar el modelo entrenado
        joblib.dump(modelo, 'random_forest_model_costos_totales.pkl')
        print("Modelo de Random Forest para costos totales guardado con éxito.")
    else:
        print("No hay suficientes datos para entrenar el modelo.")

# Función para entrenar el modelo Random Forest para estudios
def entrenar_random_forest_para_estudios():
    """
    Esta función entrena un modelo de Random Forest para predecir la cantidad de estudios realizados por los afiliados, 
    basándose en su edad y plan, utilizando los datos de estudios médicos y afiliados.
    """
    estudios = EstudioProcedimiento.objects.all().values()
    afiliados = Afiliado.objects.all().values()

    # Convertir a DataFrame
    df_estudios = pd.DataFrame(estudios)
    df_afiliados = pd.DataFrame(afiliados)

    # Realizar el merge entre estudios y afiliados
    df_estudios['patient_id'] = df_estudios['patient_id'].apply(lambda x: f"AF-{str(x).zfill(4)}")
    df = pd.merge(df_estudios, df_afiliados, left_on='patient_id', right_on='affiliate_id', how='inner')

    if df.shape[0] == 0:
        print("No se encontraron registros coincidentes entre estudios y afiliados.")
        return None

    # Generar la variable objetivo (cantidad de estudios)
    df['cantidad_estudios'] = df.groupby('affiliate_id')['procedure_id'].transform('count')

    # Convertir variables categóricas
    label_encoder = LabelEncoder()
    df['plan'] = label_encoder.fit_transform(df['plan'])
    df['grupo_edad'] = label_encoder.fit_transform(pd.cut(df['age'], bins=[0, 18, 35, 50, 65, 100], labels=['0-18', '19-35', '36-50', '51-65', '66+']))

    # Características de entrada (X)
    X = df[['age', 'plan', 'grupo_edad']]
    y = df['cantidad_estudios']

    # Dividir los datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crear y entrenar el modelo de Random Forest
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
    if modelo_estudios:
        joblib.dump(modelo_estudios, 'random_forest_model_estudios.pkl')
        print("Modelo Random Forest para cantidad de estudios guardado como 'random_forest_model_estudios.pkl'.")
