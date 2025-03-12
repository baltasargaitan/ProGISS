import os
import django
import random

# Establecer la variable de entorno DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_giss.settings')

# Configurar Django
django.setup()

# Importar modelos después de configurar Django
from gestion_datos.models import Afiliado

def calcular_nivel_riesgo(hospitalizations, consultations, medication_cost):
    """
    Calcula el puntaje de riesgo basado en hospitalizaciones, consultas previas y costo de medicación.
    """
    risk_score = (
        (hospitalizations * 0.4) + 
        (consultations * 0.3) + 
        (medication_cost / 1000000 * 0.3)
    )
    return min(max(risk_score, 0), 1)  # Asegura que el riesgo esté entre 0 y 1

def generar_afiliados_desde_ppt():
    """
    Genera afiliados en la base de datos basándose en las estadísticas del PPT.
    """
    total_afiliados = 8310  # Número exacto de afiliados
    proporcion_capital = 0.59  # 59% de afiliados en Capital
    
    afiliados_capital = int(total_afiliados * proporcion_capital)
    afiliados_interior = total_afiliados - afiliados_capital
    
    afiliados_generados = []
    current_id = 1
    
    # Porcentajes para distribuir los afiliados en diferentes niveles de riesgo
    porcentaje_riesgo_bajo = 0.90
    porcentaje_riesgo_medio = 0.02
    porcentaje_riesgo_alto = 0.08

    # Cantidades de afiliados en cada categoría
    total_riesgo_bajo = int(total_afiliados * porcentaje_riesgo_bajo)
    total_riesgo_medio = int(total_afiliados * porcentaje_riesgo_medio)
    total_riesgo_alto = int(total_afiliados * porcentaje_riesgo_alto)

    contador_riesgo_bajo = contador_riesgo_medio = contador_riesgo_alto = 0

    def crear_afiliado(region):
        nonlocal current_id, contador_riesgo_bajo, contador_riesgo_medio, contador_riesgo_alto
        
        affiliate_id = f"AF-{str(current_id).zfill(4)}"
        chronic_condition = current_id > 5395
        
        if contador_riesgo_bajo < total_riesgo_bajo:
            # Riesgo bajo: pocas hospitalizaciones
            previous_hospitalizations = 0
            previous_consultations = max(0, random.gauss(2.0, 0.5))  # Pocas consultas
            previous_medication_cost = random.uniform(0, 30000)  # Bajo costo de medicación
            contador_riesgo_bajo += 1
        elif contador_riesgo_medio < total_riesgo_medio:
            # Riesgo medio: hospitalizaciones de 1-2, algunas consultas y medicación moderada
            previous_hospitalizations = random.choice([1, 2])
            previous_consultations = max(0, random.gauss(3.45, 1))  # Promedio de consultas
            previous_medication_cost = random.uniform(30000, 100000)  # Costo moderado de medicación
            contador_riesgo_medio += 1
        elif contador_riesgo_alto < total_riesgo_alto:
            # Riesgo alto: muchas hospitalizaciones, muchas consultas y alto costo de medicación
            previous_hospitalizations = random.randint(5, 10)
            previous_consultations = max(0, random.gauss(7.0, 2))  # Más consultas
            previous_medication_cost = random.uniform(100000, 1000000)  # Alto costo de medicación
            contador_riesgo_alto += 1
        else:
            # Si ya se alcanzaron los límites de riesgo, asignar riesgo bajo por defecto
            previous_hospitalizations = 0
            previous_consultations = max(0, random.gauss(2.0, 0.5))
            previous_medication_cost = random.uniform(0, 30000)
        
        risk_score = calcular_nivel_riesgo(previous_hospitalizations, previous_consultations, previous_medication_cost)
        
        afiliado = Afiliado(
            id=current_id,
            affiliate_id=affiliate_id,
            age=random.randint(0, 19) if current_id <= 2407 else random.randint(20, 45) if current_id <= 4807 else random.randint(46, 70),
            sex=random.choice(["Masculino", "Femenino"]),
            chronic_condition=chronic_condition,
            region=region,
            previous_consultations=previous_consultations,
            previous_hospitalizations=previous_hospitalizations,
            previous_medication_cost=previous_medication_cost,
            enrolled_in_program=random.choice([True, False]),
            risk_score=risk_score,
            plan=random.choice(["Básico", "Regular", "Avanzado", "Premium"]),
        )
        current_id += 1
        return afiliado

    for _ in range(afiliados_capital):
        afiliados_generados.append(crear_afiliado("Capital"))
    
    for _ in range(afiliados_interior):
        afiliados_generados.append(crear_afiliado("Interior"))
    
    Afiliado.objects.bulk_create(afiliados_generados)
    print(f"{len(afiliados_generados)} afiliados generados con éxito según datos del PPT.")

generar_afiliados_desde_ppt()
