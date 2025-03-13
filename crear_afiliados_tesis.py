import os

import random
import django
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
    Genera afiliados en la base de datos asegurando que el 60% tenga plan Básico y el 40% plan Premium.
    """
    total_afiliados = 8310
    proporcion_capital = 0.59
    
    afiliados_capital = int(total_afiliados * proporcion_capital)
    afiliados_interior = total_afiliados - afiliados_capital
    
    afiliados_generados = []
    current_id = 1
    
    porcentaje_riesgo_bajo = 0.90
    porcentaje_riesgo_medio = 0.02
    porcentaje_riesgo_alto = 0.08

    total_riesgo_bajo = int(total_afiliados * porcentaje_riesgo_bajo)
    total_riesgo_medio = int(total_afiliados * porcentaje_riesgo_medio)
    total_riesgo_alto = int(total_afiliados * porcentaje_riesgo_alto)

    contador_riesgo_bajo = contador_riesgo_medio = contador_riesgo_alto = 0
    
    # Forzar cantidades de planes
    total_basico = int(total_afiliados * 0.60)
    total_premium = total_afiliados - total_basico

    contador_basico = contador_premium = 0

    def crear_afiliado(region):
        nonlocal current_id, contador_riesgo_bajo, contador_riesgo_medio, contador_riesgo_alto
        nonlocal contador_basico, contador_premium

        affiliate_id = f"AF-{str(current_id).zfill(4)}"
        age = random.randint(0, 19) if current_id <= 2407 else random.randint(20, 45) if current_id <= 4807 else random.randint(46, 70)
        chronic_condition = current_id > 5395

        if contador_riesgo_bajo < total_riesgo_bajo:
            previous_hospitalizations = 0
            previous_consultations = max(0, random.gauss(2.0, 0.5))
            previous_medication_cost = random.uniform(0, 30000)
            contador_riesgo_bajo += 1
        elif contador_riesgo_medio < total_riesgo_medio:
            previous_hospitalizations = random.choice([1, 2])
            previous_consultations = max(0, random.gauss(3.45, 1))
            previous_medication_cost = random.uniform(30000, 100000)
            contador_riesgo_medio += 1
        elif contador_riesgo_alto < total_riesgo_alto:
            previous_hospitalizations = random.randint(5, 10)
            previous_consultations = max(0, random.gauss(7.0, 2))
            previous_medication_cost = random.uniform(100000, 1000000)
            contador_riesgo_alto += 1
        else:
            previous_hospitalizations = 0
            previous_consultations = max(0, random.gauss(2.0, 0.5))
            previous_medication_cost = random.uniform(0, 30000)

        risk_score = calcular_nivel_riesgo(previous_hospitalizations, previous_consultations, previous_medication_cost)

        # Asignación de planes con la condición del 80% de mayores de 40 años en plan Premium
        if age > 40:
            plan = "Premium" if random.random() < 0.80 else "Básico"
        else:
            plan = "Básico" if contador_basico < total_basico else "Premium"

        if plan == "Básico":
            contador_basico += 1
        else:
            contador_premium += 1

        afiliado = Afiliado(
            id=current_id,
            affiliate_id=affiliate_id,
            age=age,
            sex=random.choice(["Masculino", "Femenino"]),
            chronic_condition=chronic_condition,
            region=region,
            previous_consultations=previous_consultations,
            previous_hospitalizations=previous_hospitalizations,
            previous_medication_cost=previous_medication_cost,
            enrolled_in_program=random.choice([True, False]),
            risk_score=risk_score,
            plan=plan,
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
