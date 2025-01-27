import csv
from django.shortcuts import render
from django.http import HttpResponse
from matplotlib import pyplot as plt
from .models import Afiliado
from django.db.models import Sum, Count, Avg
import pandas as pd
import joblib
from io import BytesIO
import base64
import csv
from django.http import HttpResponse
import joblib
import pandas as pd
from .models import Afiliado
from openpyxl import Workbook
from django.http import HttpResponse
import joblib
import pandas as pd
from .models import Afiliado
import plotly.express as px
import joblib
import pandas as pd
from django.shortcuts import render
from .models import Afiliado


# -------------------------------
# Vista de inicio
# -------------------------------
def inicio(request):
    """
    Página de bienvenida de la aplicación.
    """
    return HttpResponse("<h1>Bienvenido a ProGISS</h1><p>Esta es la página inicial de la aplicación.</p>")



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
# Dashboard Principal
# -------------------------------
def dashboard(request):
    """
    Muestra estadísticas generales y lista de afiliados.
    """
    afiliados = Afiliado.objects.all()
    stats = {
        'total_afiliados': afiliados.count(),
        'promedio_edad': afiliados.aggregate(Avg('age'))['age__avg'],
        'consultas_totales': afiliados.aggregate(Sum('previous_consultations'))['previous_consultations__sum'],
        'hospitalizaciones_totales': afiliados.aggregate(Sum('previous_hospitalizations'))['previous_hospitalizations__sum'],
    }
    return render(request, 'gestion_datos/dashboard.html', {'stats': stats, 'afiliados': afiliados})

# -------------------------------
# Consultas por Categoría
# -------------------------------
def consultas_categoria(request):
    """
    Agrupa consultas médicas por región y grupo etario.
    """
    consultas_por_region = Afiliado.objects.values('region').annotate(
        total_consultas=Sum('previous_consultations')
    )

    grupos_etarios = {
        'Menores de 30': Afiliado.objects.filter(age__lt=30).aggregate(Sum('previous_consultations'))['previous_consultations__sum'] or 0,
        '30-50': Afiliado.objects.filter(age__gte=30, age__lte=50).aggregate(Sum('previous_consultations'))['previous_consultations__sum'] or 0,
        'Mayores de 50': Afiliado.objects.filter(age__gt=50).aggregate(Sum('previous_consultations'))['previous_consultations__sum'] or 0,
    }

    return render(request, 'gestion_datos/consultas_categoria.html', {
        'consultas_por_region': consultas_por_region,
        'grupos_etarios': grupos_etarios
    })

# -------------------------------
# Hospitalizaciones Proyectadas
# -------------------------------


def hospitalizaciones_proyectadas(request):
    """
    Predice hospitalizaciones futuras y las agrupa por región y grupo etario.
    """
    # Cargar el modelo de predicción
    logistic_model = joblib.load('logistic_model.pkl')

    # Obtener los datos de los afiliados
    afiliados = Afiliado.objects.all()
    data = pd.DataFrame(list(afiliados.values('id', 'age', 'previous_consultations', 'previous_medication_cost', 'region')))

    # Realizar la predicción de hospitalizaciones
    data['hospitalizacion_predicha'] = logistic_model.predict(
        data[['age', 'previous_consultations', 'previous_medication_cost']]
    )

    # Agrupar hospitalizaciones por región
    hospitalizaciones_por_region = data.groupby('region')['hospitalizacion_predicha'].sum().reset_index()

    # Crear el gráfico de hospitalizaciones por región
    fig_region = px.bar(
        hospitalizaciones_por_region,
        x='region',
        y='hospitalizacion_predicha',
        title='Hospitalizaciones Proyectadas por Región',
        labels={'hospitalizacion_predicha': 'Hospitalizaciones Proyectadas', 'region': 'Región'}
    )

    # Agrupar hospitalizaciones por grupo etario
    data['grupo_etario'] = pd.cut(
        data['age'], bins=[0, 30, 50, 100], labels=['Menores de 30', '30-50', 'Mayores de 50']
    )
    hospitalizaciones_por_grupo = data.groupby('grupo_etario')['hospitalizacion_predicha'].sum().reset_index()

    # Crear el gráfico de hospitalizaciones por grupo etario
    fig_grupo = px.bar(
        hospitalizaciones_por_grupo,
        x='grupo_etario',
        y='hospitalizacion_predicha',
        title='Hospitalizaciones Proyectadas por Grupo Etario',
        labels={'hospitalizacion_predicha': 'Hospitalizaciones Proyectadas', 'grupo_etario': 'Grupo Etario'}
    )

    # Convertir los gráficos a HTML para integrarlos en la plantilla
    graph_region = fig_region.to_html(full_html=False)
    graph_grupo = fig_grupo.to_html(full_html=False)

    # Pasar los gráficos y los datos a la plantilla
    return render(request, 'gestion_datos/hospitalizaciones_proyectadas.html', {
        'hospitalizaciones_por_region': hospitalizaciones_por_region.to_dict(orient='records'),
        'hospitalizaciones_por_grupo': hospitalizaciones_por_grupo.to_dict(orient='records'),
        'graph_region': graph_region,
        'graph_grupo': graph_grupo,
    })



def exportar_predicciones(request):
    """
    Genera un archivo Excel con predicciones para los afiliados seleccionados,
    sin caracteres especiales para compatibilidad.
    """
    if request.method == "POST":
        afiliado_ids = request.POST.getlist('afiliados')

        if not afiliado_ids:
            return HttpResponse("No affiliates selected.", content_type="text/plain")

        # Cargar modelos entrenados
        logistic_model = joblib.load('logistic_model.pkl')
        random_forest_model = joblib.load('random_forest_model.pkl')

        # Crear un archivo Excel
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Predictions"

        # Escribir encabezados (sin caracteres especiales)
        headers = [
            'Affiliate_ID', 'Age', 'Region', 'Previous_Consultations',
            'Previous_Hospitalizations', 'Medication_Cost',
            'Hospitalization_Prediction', 'Consultation_Prediction'
        ]
        worksheet.append(headers)

        # Generar predicciones
        for afiliado_id in afiliado_ids:
            afiliado = Afiliado.objects.get(id=afiliado_id)

            # Crear DataFrame con datos del afiliado
            data = pd.DataFrame([{
                'age': afiliado.age,
                'previous_consultations': afiliado.previous_consultations,
                'previous_hospitalizations': afiliado.previous_hospitalizations,
                'previous_medication_cost': afiliado.previous_medication_cost,
            }])

            # Predicciones
            prediccion_hospitalizacion = logistic_model.predict(
                data[['age', 'previous_consultations', 'previous_medication_cost']]
            )[0]

            prediccion_consultas = random_forest_model.predict(
                data[['age', 'previous_hospitalizations', 'previous_medication_cost']]
            )[0]

            # Escribir fila en Excel (sin caracteres especiales)
            worksheet.append([
                afiliado.affiliate_id, afiliado.age, afiliado.region,
                afiliado.previous_consultations, afiliado.previous_hospitalizations,
                afiliado.previous_medication_cost,
                "Yes" if prediccion_hospitalizacion == 1 else "No",
                round(prediccion_consultas, 2)
            ])

        # Configurar la respuesta HTTP con el archivo Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="affiliate_predictions.xlsx"'
        workbook.save(response)
        return response

# -------------------------------
# Exportar Datos para BI
# -------------------------------
def exportar_datos_csv(request):
    """
    Exporta los datos de afiliados en formato CSV para uso en Power BI o Google Data Studio.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="datos_afiliados.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Affiliate_ID', 'Age', 'Sex', 'Region', 'Chronic_Condition',
        'Previous_Consultations', 'Previous_Hospitalizations',
        'Previous_Medication_Cost', 'Enrolled_in_Program', 'Risk_Score'
    ])

    for afiliado in Afiliado.objects.all():
        writer.writerow([
            afiliado.affiliate_id,
            afiliado.age,
            afiliado.sex,
            afiliado.region,
            "Yes" if afiliado.chronic_condition else "No",
            afiliado.previous_consultations,
            afiliado.previous_hospitalizations,
            afiliado.previous_medication_cost,
            "Yes" if afiliado.enrolled_in_program else "No",
            afiliado.risk_score
        ])

    return response


def segmentacion(request):
    """
    Segmenta a los afiliados en niveles de riesgo según criterios predefinidos.
    """
    riesgo_bajo = Afiliado.objects.filter(age__lt=40, chronic_condition=False).count()
    riesgo_medio = Afiliado.objects.filter(chronic_condition=True, previous_consultations__gt=3).count()
    riesgo_alto = Afiliado.objects.filter(
        chronic_condition=True,
        previous_hospitalizations__gte=1,
        previous_medication_cost__gt=1000
    ).count()

    # Crear un gráfico de pastel para la segmentación
    labels = ['Riesgo Bajo', 'Riesgo Medio', 'Riesgo Alto']
    sizes = [riesgo_bajo, riesgo_medio, riesgo_alto]
    colors = ['green', 'orange', 'red']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
    plt.title('Distribución de Niveles de Riesgo')

    # Convertir gráfico a formato base64 para mostrar en HTML
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
        'grafico_base64': image_base64
    })


def predicciones_cliente(request, id):
    """
    Genera predicciones específicas para un afiliado basado en su ID.
    """
    try:
        afiliado = Afiliado.objects.get(id=id)
    except Afiliado.DoesNotExist:
        return HttpResponse("Afiliado no encontrado", status=404)

    logistic_model = joblib.load('logistic_model.pkl')
    random_forest_model = joblib.load('random_forest_model.pkl')

    # Crear DataFrame con los datos del afiliado
    data = pd.DataFrame([{
        'age': afiliado.age,
        'previous_consultations': afiliado.previous_consultations,
        'previous_hospitalizations': afiliado.previous_hospitalizations,
        'previous_medication_cost': afiliado.previous_medication_cost
    }])

    # Predicciones
    prediccion_hospitalizacion = logistic_model.predict(data[['age', 'previous_consultations', 'previous_medication_cost']])[0]
    prediccion_consultas = random_forest_model.predict(data[['age', 'previous_hospitalizations', 'previous_medication_cost']])[0]

    return render(request, 'gestion_datos/predicciones_cliente.html', {
        'afiliado': afiliado,
        'prediccion_hospitalizacion': "Yes" if prediccion_hospitalizacion == 1 else "No",
        'prediccion_consultas': round(prediccion_consultas, 2)
    })

import joblib
import pandas as pd
import plotly.express as px
from django.shortcuts import render
from .models import Afiliado
import joblib
import pandas as pd
import plotly.express as px
from django.shortcuts import render
from .models import Afiliado

def costos_medicos_proyectados(request):
    """
    Predice los costos de medicamentos futuros y los agrupa por región y grupo etario.
    """
    # Cargar el modelo de predicción de costos de medicamentos
    random_forest_model = joblib.load('random_forest_model.pkl')  # Asegúrate de que la ruta sea correcta

    # Obtener los datos de los afiliados
    afiliados = Afiliado.objects.all()
    data = pd.DataFrame(list(afiliados.values('affiliate_id', 'age', 'previous_hospitalizations', 'previous_medication_cost', 'previous_consultations', 'region')))

    # Realizar la predicción de costos de medicamentos solo con las columnas correctas
    # Asegúrate de usar las mismas columnas que usaste para entrenar el modelo
    X = data[['age', 'previous_hospitalizations', 'previous_medication_cost']]  # Usa las mismas columnas que en el entrenamiento
    data['costo_medico_predicho'] = random_forest_model.predict(X)

    # Agrupar los costos proyectados por región
    costos_por_region = data.groupby('region')['costo_medico_predicho'].sum().reset_index()

    # Crear el gráfico de costos de medicamentos proyectados por región
    fig_region = px.bar(
        costos_por_region,
        x='region',
        y='costo_medico_predicho',
        title='Costos Proyectados de Medicamentos por Región',
        labels={'costo_medico_predicho': 'Costo de Medicamentos Proyectado'},
        color='region'
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

    # Renderizar los gráficos en la plantilla
    return render(request, 'gestion_datos/costos_medicos.html', {
        'fig_region': fig_region.to_html(full_html=False),
        'fig_edad': fig_edad.to_html(full_html=False)
    })







def error_view(request, message="Algo salió mal."):
    return render(request, 'error.html', {'message': message})
