import csv
from django.shortcuts import render
from django.http import HttpResponse
from matplotlib import pyplot as plt
from sklearn.calibration import LabelEncoder
from .models import Afiliado, EstudioProcedimiento
from django.db.models import Sum, Count, Avg
import pandas as pd
import joblib
from io import BytesIO
import base64
from openpyxl import Workbook
import matplotlib
matplotlib.use('Agg')
import plotly.express as px
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
plt.switch_backend('Agg')

# -------------------------------
# Vista de inicio
# -------------------------------

def inicio(request):
    """
    Página de bienvenida de la aplicación con animación y sidebar.
    """
    return render(request, 'gestion_datos/inicio.html')


# -------------------------------
# Dashboard Principal
# -------------------------------

def dashboard(request):
    """
    Muestra estadísticas generales y lista de afiliados.
    """
    afiliados = Afiliado.objects.all().order_by('id') 
    
    # Paginación
    paginator = Paginator(afiliados, 100)  # 100 afiliados por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Estadísticas
    stats = {
        'total_afiliados': afiliados.count(),
        'promedio_edad': afiliados.aggregate(Avg('age'))['age__avg'],
        'consultas_totales': afiliados.aggregate(Sum('previous_consultations'))['previous_consultations__sum'],
        'hospitalizaciones_totales': afiliados.aggregate(Sum('previous_hospitalizations'))['previous_hospitalizations__sum'],
    }

    return render(request, 'gestion_datos/dashboard.html', {'stats': stats, 'page_obj': page_obj})


# -------------------------------
# Vista de detalle de afiliado
# -------------------------------
def detalle_afiliado(request, id):
    """
    Muestra los detalles de un afiliado específico basado en su ID.
    """
    try:
        afiliado = Afiliado.objects.get(id=id)
    except Afiliado.DoesNotExist:
        return HttpResponse("Afiliado no encontrado", status=404)

    return render(request, 'gestion_datos/detalle_afiliado.html', {'afiliado': afiliado})


# -------------------------------
# Consultas por Categoría
# -------------------------------
def consultas_categoria(request):
    """
    Agrupa consultas médicas por plan y grupo etario.
    """
    consultas_por_plan = Afiliado.objects.values('plan').annotate(
        total_consultas=Sum('previous_consultations')
    )

    grupos_etarios = {
        'Menores de 30': Afiliado.objects.filter(age__lt=30).aggregate(Sum('previous_consultations'))['previous_consultations__sum'] or 0,
        '30-50': Afiliado.objects.filter(age__gte=30, age__lte=50).aggregate(Sum('previous_consultations'))['previous_consultations__sum'] or 0,
        'Mayores de 50': Afiliado.objects.filter(age__gt=50).aggregate(Sum('previous_consultations'))['previous_consultations__sum'] or 0,
    }

    return render(request, 'gestion_datos/consultas_categoria.html', {
        'consultas_por_plan': consultas_por_plan,
        'grupos_etarios': grupos_etarios
    })

# -------------------------------
# Hospitalizaciones Proyectadas
# -------------------------------
def hospitalizaciones_proyectadas(request):
    """
    Predice hospitalizaciones futuras y las agrupa por plan y grupo etario.
    """
    logistic_model = joblib.load('logistic_model.pkl')
    afiliados = Afiliado.objects.all()
    data = pd.DataFrame(list(afiliados.values('id', 'age', 'previous_consultations', 'previous_medication_cost', 'plan')))

    data['hospitalizacion_predicha'] = logistic_model.predict(
        data[['age', 'previous_consultations', 'previous_medication_cost']])
    
    # Agrupar por plan en vez de región
    hospitalizaciones_por_plan = data.groupby('plan')['hospitalizacion_predicha'].sum().reset_index()

    fig_plan = px.bar(
        hospitalizaciones_por_plan,
        x='plan',
        y='hospitalizacion_predicha',
        title='Hospitalizaciones Proyectadas por Plan',
        labels={'hospitalizacion_predicha': 'Hospitalizaciones Proyectadas', 'plan': 'Plan'}
    )

    data['grupo_etario'] = pd.cut(
        data['age'], bins=[0, 30, 50, 100], labels=['Menores de 30', '30-50', 'Mayores de 50']
    )
    hospitalizaciones_por_grupo = data.groupby('grupo_etario')['hospitalizacion_predicha'].sum().reset_index()

    fig_grupo = px.bar(
        hospitalizaciones_por_grupo,
        x='grupo_etario',
        y='hospitalizacion_predicha',
        title='Hospitalizaciones Proyectadas por Grupo Etario',
        labels={'hospitalizacion_predicha': 'Hospitalizaciones Proyectadas', 'grupo_etario': 'Grupo Etario'}
    )

    graph_plan = fig_plan.to_html(full_html=False)
    graph_grupo = fig_grupo.to_html(full_html=False)

    return render(request, 'gestion_datos/hospitalizaciones_proyectadas.html', {
        'hospitalizaciones_por_plan': hospitalizaciones_por_plan.to_dict(orient='records'),
        'hospitalizaciones_por_grupo': hospitalizaciones_por_grupo.to_dict(orient='records'),
        'graph_plan': graph_plan,
        'graph_grupo': graph_grupo,
    })


# -------------------------------
# Exportar Predicciones
# -------------------------------
def exportar_predicciones(request):
    """
    Genera un archivo Excel con predicciones para todos los afiliados.
    """
    if request.method == "POST":
        logistic_model = joblib.load('logistic_model.pkl')
        random_forest_model_consultas = joblib.load('random_forest_model_consultas.pkl')

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Predictions"

        headers = [
            'Affiliate_ID', 'Age', 'Region', 'Previous_Consultations',
            'Previous_Hospitalizations', 'Medication_Cost',
            'Hospitalization_Prediction', 'Consultation_Prediction'
        ]
        worksheet.append(headers)

        afiliados = Afiliado.objects.all()

        for afiliado in afiliados:
            data = pd.DataFrame([{
                'age': afiliado.age,
                'previous_consultations': afiliado.previous_consultations,
                'previous_hospitalizations': afiliado.previous_hospitalizations,
                'previous_medication_cost': afiliado.previous_medication_cost,
            }])

            prediccion_hospitalizacion = logistic_model.predict(
                data[['age', 'previous_consultations', 'previous_medication_cost']])[0]

            prediccion_consultas = random_forest_model_consultas.predict(
                data[['age', 'previous_hospitalizations', 'previous_medication_cost']])[0]

            worksheet.append([  
                afiliado.affiliate_id, afiliado.age, afiliado.region,
                afiliado.previous_consultations, afiliado.previous_hospitalizations,
                afiliado.previous_medication_cost,
                "Yes" if prediccion_hospitalizacion == 1 else "No",
                round(prediccion_consultas, 2)
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="affiliate_predictions.xlsx"'
        workbook.save(response)
        return response

    return HttpResponse("Invalid request method.", content_type="text/plain")


# -------------------------------
# Segmentación de Afiliados
# -------------------------------
def segmentacion(request):
    """
    Segmenta a los afiliados en niveles de riesgo según criterios predefinidos.
    """
    # Calcular afiliados de riesgo alto (con condición crónica, más de 1 hospitalización y más de 1000 en costo de medicación)
    riesgo_alto = Afiliado.objects.filter(
        chronic_condition=True,
        previous_hospitalizations__gte=1,
        previous_medication_cost__gte=1000
    ).count()
    print("Riesgo Alto:", riesgo_alto)

    # Calcular afiliados de riesgo medio (con condición crónica y más de 2 consultas, sin ser alto)
    riesgo_medio = Afiliado.objects.filter(
        chronic_condition=True,
        previous_consultations__gte=2
    ).exclude(
        chronic_condition=True,
        previous_hospitalizations__gte=1,
        previous_medication_cost__gte=1000  # Excluye a los que ya son altos
    ).count()
    print("Riesgo Medio:", riesgo_medio)
    
    # Calcular afiliados de riesgo bajo (menores de 40 años, sin condición crónica, sin ser medio o alto)
    riesgo_bajo = Afiliado.objects.filter(
        age__lt=40, 
        chronic_condition=False
    ).exclude(
        chronic_condition=True,
        previous_consultations__gte=2,  # Excluye a los que tienen más de 2 consultas (medio)
        previous_hospitalizations__gte=1,  # Excluye a los que tienen hospitalizaciones (alto)
        previous_medication_cost__gte=1000  # Excluye a los que tienen costos altos de medicación (alto)
    ).count()
    print("Riesgo Bajo:", riesgo_bajo)

    # Verificar el total de afiliados
    total_afiliados = Afiliado.objects.count()
    print("Total Afiliados:", total_afiliados)

    # Asegurarnos de que los porcentajes sumen al 100%
    no_asignado = total_afiliados - (riesgo_bajo + riesgo_medio + riesgo_alto)
    if no_asignado < 0: 
        no_asignado = 0  # Evitar valores negativos en caso de error de cálculo

    # Etiquetas y valores para el gráfico
    labels = ['Riesgo Bajo', 'Riesgo Medio', 'Riesgo Alto', 'No Asignado']
    sizes = [riesgo_bajo, riesgo_medio, riesgo_alto, no_asignado]
    colors = ['green', 'orange', 'red', 'gray']  # Color para 'No Asignado'

    # Crear el gráfico
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
    plt.title('Distribución de Niveles de Riesgo')

    # Convertir la imagen a base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'gestion_datos/segmentacion.html', {
        'riesgo_bajo': riesgo_bajo,
        'riesgo_medio': riesgo_medio,
        'riesgo_alto': riesgo_alto,
        'grafico_base64': image_base64,
        'total_afiliados': total_afiliados,
        'no_asignado': no_asignado
    })


def predicciones_cliente(request, id):
    """
    Genera predicciones específicas para un afiliado basado en su ID.
    """
    try:
        # Obtener el afiliado y sus datos
        afiliado = Afiliado.objects.get(id=id)
    except Afiliado.DoesNotExist:
        return HttpResponse("Afiliado no encontrado", status=404)

    # Cargar los modelos entrenados
    logistic_model = joblib.load('logistic_model.pkl')
    random_forest_model_consultas = joblib.load('random_forest_model_consultas.pkl')
    modelo_estudios = joblib.load('random_forest_model_estudios.pkl')

    # Obtener los datos del afiliado para la predicción
    data = pd.DataFrame([{
        'age': afiliado.age,
        'previous_consultations': afiliado.previous_consultations,
        'previous_hospitalizations': afiliado.previous_hospitalizations,
        'previous_medication_cost': afiliado.previous_medication_cost
    }])

    # Realizar las predicciones
    prediccion_hospitalizacion = logistic_model.predict(data[['age', 'previous_consultations', 'previous_medication_cost']])[0]
    prediccion_consultas = random_forest_model_consultas.predict(data[['age', 'previous_hospitalizations', 'previous_medication_cost']])[0]

    # Preparar los datos para la predicción de estudios médicos
    data_estudios = {
        'age': afiliado.age,
        'plan': afiliado.plan,
        'grupo_edad': pd.cut([afiliado.age], bins=[0, 18, 35, 50, 65, 100], labels=['0-18', '19-35', '36-50', '51-65', '66+'])[0]
    }

    # Convertir las variables categóricas
    label_encoder = LabelEncoder()
    data_estudios['plan'] = label_encoder.fit_transform([data_estudios['plan']])[0]
    data_estudios['grupo_edad'] = label_encoder.fit_transform([data_estudios['grupo_edad']])[0]

    # Convertir los datos en un DataFrame
    df_estudios = pd.DataFrame([data_estudios])

    # Realizar la predicción de estudios
    prediccion_estudios = modelo_estudios.predict(df_estudios)

    # Mostrar las predicciones junto con los datos del afiliado
    return render(request, 'gestion_datos/predicciones_cliente.html', {
        'afiliado': afiliado,
        'prediccion_hospitalizacion': "Si" if prediccion_hospitalizacion == 1 else "No",
        'prediccion_consultas': round(prediccion_consultas, 0),
        'prediccion_estudios': round(prediccion_estudios[0],0)  # Tipo de estudio proyectado
    })


# -------------------------------
# Costos Médicos Proyectados
# -------------------------------
def costos_medicos_proyectados(request):
    """
    Predice los costos de medicamentos futuros y los agrupa por plan y grupo etario.
    """
    random_forest_model_costos = joblib.load('random_forest_model_costos.pkl')
    # Obtener los datos de los afiliados
    afiliados = Afiliado.objects.all()
    data = pd.DataFrame(list(afiliados.values('affiliate_id', 'age', 'previous_hospitalizations', 'previous_consultations', 'plan')))

    # Realizar la predicción de costos de medicamentos
    X = data[['age', 'previous_hospitalizations', 'previous_consultations']]  
    data['costo_medico_predicho'] = random_forest_model_costos.predict(X)

    # Agrupar los costos proyectados por plan
    costos_por_plan = data.groupby('plan')['costo_medico_predicho'].sum().reset_index()

    # Crear el gráfico de costos de medicamentos proyectados por plan
    fig_plan = px.bar(
        costos_por_plan,
        x='plan',
        y='costo_medico_predicho',
        title='Costos Proyectados de Medicamentos por Plan',
        labels={'costo_medico_predicho': 'Costo de Medicamentos Proyectado'},
        color='plan'
    )

    # Agrupar los costos proyectados por grupo de edad
    data['grupo_etario'] = pd.cut(data['age'], bins=[0, 18, 40, 60, 100], labels=['0-18', '19-40', '41-60', '61+'])
    costos_por_edad = data.groupby('grupo_etario')['costo_medico_predicho'].sum().reset_index()

    # Crear el gráfico de costos de medicamentos proyectados por grupo etario
    fig_edad = px.bar(
        costos_por_edad,
        x='grupo_etario',
        y='costo_medico_predicho',
        title='Costos Proyectados de Medicamentos por Grupo Etario',
        labels={'costo_medico_predicho': 'Costo de Medicamentos Proyectado'},
        color='grupo_etario'
    )

    return render(request, 'gestion_datos/costos_medicos_proyectados.html', {
        'costos_por_plan': costos_por_plan.to_dict(orient='records'),
        'costos_por_edad': costos_por_edad.to_dict(orient='records'),
        'graph_plan': fig_plan.to_html(full_html=False),
        'graph_edad': fig_edad.to_html(full_html=False),
    })


# -------------------------------
# Costos Totales Proyectados
# -------------------------------
def costos_totales_proyectados(request):
    """
    Predice los costos totales proyectados de cada afiliado, sumando los costos de hospitalización y medicamentos.
    """
    # Cargar los modelos previamente entrenados
    logistic_model = joblib.load('logistic_model.pkl')  # Modelo para hospitalización
    random_forest_model_costos = joblib.load('random_forest_model_costos.pkl')  # Modelo para costos de medicamentos

    # Obtener los datos de los afiliados
    afiliados = Afiliado.objects.all()
    data = pd.DataFrame(list(afiliados.values('affiliate_id', 'age', 'previous_hospitalizations', 'previous_consultations', 'previous_medication_cost', 'plan')))  # Cambié 'region' por 'plan'

    # Predicción de hospitalización
    data['hospitalizacion_predicha'] = logistic_model.predict(
        data[['age', 'previous_consultations', 'previous_medication_cost']])
    
    # Predicción de costos de medicamentos
    X = data[['age', 'previous_hospitalizations', 'previous_consultations']]
    data['costo_medico_predicho'] = random_forest_model_costos.predict(X)

    # Sumar ambos costos: hospitalización y medicamentos para obtener el costo total proyectado
    data['costo_total_proyectado'] = data['hospitalizacion_predicha'] * 5000 + data['costo_medico_predicho']  # Asumimos un costo fijo por hospitalización

    # Agrupar por plan y obtener la suma de los costos proyectados por cada plan
    costos_por_plan = data.groupby('plan')['costo_total_proyectado'].sum().reset_index()  # Cambié 'region' por 'plan'

    # Crear un gráfico interactivo con Plotly
    fig_plan = px.bar(
        costos_por_plan,
        x='plan',
        y='costo_total_proyectado',
        title='Costos Totales Proyectados por Plan',
        labels={'costo_total_proyectado': 'Costo Total Proyectado (en $)', 'plan': 'Plan'},
        color='plan'
    )

    # Renderizar la plantilla con los datos y el gráfico
    return render(request, 'gestion_datos/costos_totales_proyectados.html', {
        'costos_por_plan': costos_por_plan.to_dict(orient='records'),
        'graph_plan': fig_plan.to_html(full_html=False)
    })



def error_view(request, message="Algo salió mal."):
    return render(request, 'error.html', {'message': message}) # vista por si salta un error , recordar implementar en las demas vistas...


def proyeccion_estudios(request):
    """
    Calcula la proyección de estudios usando el modelo RandomForest para cada tipo de estudio y plan.
    """
    # Cargar el modelo entrenado de Random Forest para la cantidad de estudios
    modelo_estudios = joblib.load('random_forest_model_estudios.pkl')

    # Consultamos los datos de los estudios y afiliados
    estudios = EstudioProcedimiento.objects.all().values()
    afiliados = Afiliado.objects.all().values()

    # Convertimos a DataFrame
    df_estudios = pd.DataFrame(estudios)
    df_afiliados = pd.DataFrame(afiliados)

    # Aseguramos que 'patient_id' y 'affiliate_id' tengan el mismo formato
    df_estudios['patient_id'] = df_estudios['patient_id'].apply(lambda x: f"AF-{str(x).zfill(4)}")

    # Realizamos el merge usando las claves
    df = pd.merge(df_estudios, df_afiliados, left_on='patient_id', right_on='affiliate_id')

    # Segmentar por edad
    df['grupo_edad'] = pd.cut(df['age'], bins=[0, 18, 35, 50, 65, 100], labels=['0-18', '19-35', '36-50', '51-65', '66+'])

    # Convertir variables categóricas
    label_encoder = LabelEncoder()
    df['plan'] = label_encoder.fit_transform(df['plan'])
    df['grupo_edad'] = label_encoder.fit_transform(df['grupo_edad'])

    # Características de entrada (X)
    X = df[['age', 'plan', 'grupo_edad']]

    # Predecir la cantidad de estudios
    df['cantidad_estudios_predicha'] = modelo_estudios.predict(X)

    # Agrupar por tipo de estudio y plan para la proyección de estudios
    estudios_por_tipo = df.groupby(['study_type'])['cantidad_estudios_predicha'].sum().reset_index()
    estudios_por_plan = df.groupby(['plan'])['cantidad_estudios_predicha'].sum().reset_index()

    # Crear el gráfico de proyección de estudios por tipo de estudio
    fig_tipo_estudio = px.bar(
        estudios_por_tipo,
        x='study_type',
        y='cantidad_estudios_predicha',

        labels={'cantidad_estudios_predicha': 'Cantidad de Estudios Proyectados', 'study_type': 'Tipo de Estudio'}
    )
    # Convertir los gráficos a formato HTML
    graph_tipo_estudio = fig_tipo_estudio.to_html(full_html=False)


    # Crear un diccionario con los nombres de los planes y sus cantidades de estudios
    plan_names = {0: 'Básico', 1: 'Regular', 2: 'Avanzado', 3: 'Premium'}
    estudios_por_plan['plan_nombre'] = estudios_por_plan['plan'].map(plan_names)

    # Convertir la información de estudios por plan a un formato de texto para mostrar en el template
    estudios_texto = {}
    for _, row in estudios_por_plan.iterrows():
        estudios_texto[row['plan_nombre']] = round(row['cantidad_estudios_predicha'],0)

    # Pasar el diccionario con los estudios por plan (en texto) al template
    return render(request, 'gestion_datos/proyeccion_estudios.html', {
        'graph_tipo_estudio': graph_tipo_estudio,
        'total_estudios_por_plan': estudios_texto  # Aquí usamos el nombre esperado en el template
    })
