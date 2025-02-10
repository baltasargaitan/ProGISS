import os
import django
import random

# Establecer la variable de entorno DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_giss.settings')

# Configurar Django
django.setup()

# Importar modelos después de configurar Django
from gestion_datos.models import Afiliado

# Lista de costos previos de medicamentos
costos_medicamentos = [
    32405.8, 48791.3, 12451.2, 22204.5, 39806.7, 30211, 47125, 16903, 58008,
    21205, 32405.8, 48791.3, 12451.2, 22204.5, 39806.7, 35646.38, 53670.43,
    13696.32, 24424.95, 43787.37, 33232.1, 51837.5, 18593.3, 63808.8, 23325.5,
    35646.38, 53670.43, 13696.32, 24424.95, 43787.37, 31543.2, 42986.7, 16204.5,
    18768.9, 47631.2, 29873.4, 50324.7, 11208.9, 32051.1, 21105.4, 58764.2,
    28767.7, 41501.3, 15453.4, 49002.2, 13004.4, 37506.8, 20053.3, 46988.8,
    15009.9, 2000.5, 15000, 5000, 8000, 12000, 1500, 11000, 3000, 2500, 13000,
    3500, 15000, 3200, 4800, 10000, 6000, 1800, 14000, 2200, 9000, 3000, 4700,
    11500, 7000, 13000, 2500, 8500, 12000, 11000, 8500, 10500, 3800, 9000,
    2700, 12500, 2900, 11500, 8000, 4000, 13500, 3300, 4800, 11000, 14000,
    2900, 4600, 8000, 2200, 11000, 9000
]

def generar_afiliados_desde_ppt():
    """
    Genera afiliados en la base de datos basándose en las estadísticas del PPT.
    """
    # Total de beneficiarios en 2019 según PPT
    total_afiliados = 8310  # Número exacto de afiliados
    proporcion_capital = 0.59  # 59% de afiliados en Capital
    
    afiliados_capital = int(total_afiliados * proporcion_capital)
    afiliados_interior = total_afiliados - afiliados_capital
    
    afiliados_generados = []
    current_id = 1  # Empezamos con el primer ID
    
    def crear_afiliado(region, tiene_hospitalizacion=True):
        nonlocal current_id
        
        affiliate_id = f"AF-{str(current_id).zfill(4)}"  # Formateamos el ID con ceros a la izquierda
        
        # Crear y devolver el afiliado
        afiliado = Afiliado(
            id=current_id,  # Asignamos manualmente el ID
            affiliate_id=affiliate_id,
            age=random.randint(18, 80),
            sex=random.choice(["Masculino", "Femenino"]),
            region=region,
            chronic_condition=random.choice([True, False]),
            previous_consultations=random.gauss(3.45, 0.5),  # Promedio de 3.45 consultas/año
            previous_hospitalizations=random.gauss(9.83, 1.0) if tiene_hospitalizacion else 0,
            previous_medication_cost=random.choice(costos_medicamentos),
            enrolled_in_program=random.choice([True, False]),
            risk_score=random.uniform(0, 1),  # Puntaje de riesgo aleatorio
            plan=random.choice(["Básico", "Regular", "Avanzado", "Premium"]),
        )
        current_id += 1  # Incrementamos el ID para el siguiente afiliado
        return afiliado
    
    # Crear afiliados para Capital
    for _ in range(afiliados_capital):
        tiene_hospitalizacion = random.random() > 0.3  # 70% tendrán hospitalización, 30% no
        afiliados_generados.append(crear_afiliado("Capital", tiene_hospitalizacion))
    
    # Crear afiliados para Interior
    for _ in range(afiliados_interior):
        tiene_hospitalizacion = random.random() > 0.3
        afiliados_generados.append(crear_afiliado("Interior", tiene_hospitalizacion))
    
    # Insertar afiliados en la base de datos
    Afiliado.objects.bulk_create(afiliados_generados)
    print(f"{len(afiliados_generados)} afiliados generados con éxito según datos del PPT.")

# Llamar a la función para generar los afiliados
generar_afiliados_desde_ppt()
