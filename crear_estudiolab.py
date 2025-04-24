import os
import django
import random
from uuid import uuid4
from decimal import Decimal

# Establecer variable de entorno
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_giss.settings')
django.setup()

# Importar modelos
from gestion_datos.models import LaboratorioProcedimiento, Afiliado

# Datos de distribución
distribucion = {
    'Bioquímica Clínica': {'porcentaje': 0.55, 'total': 19304, 'min_por_afiliado': 3, 'max_por_afiliado': 4},
    'Hematología': {'porcentaje': 0.25, 'total': 8775, 'min_por_afiliado': 2, 'max_por_afiliado': 3},
    'Microbiología': {'porcentaje': 0.10, 'total': 3510, 'min_por_afiliado': 2, 'max_por_afiliado': 3},
    'Laboratorio especializado': {'porcentaje': 0.10, 'total': 3510, 'min_por_afiliado': 2, 'max_por_afiliado': 3},
}

# Rango de IDs válidos
id_min = 1
id_max = 8310

def obtener_afiliado_aleatorio():
    while True:
        try:
            return Afiliado.objects.get(id=random.randint(id_min, id_max))
        except Afiliado.DoesNotExist:
            continue

def generar_costos(lab_type):
    # Ajustar rangos según tipo si es necesario
    rangos = {
        'Bioquímica Clínica': (1000, 3000),
        'Hematología': (1200, 3500),
        'Microbiología': (1500, 4000),
        'Laboratorio especializado': (2000, 5000),
    }
    minimo, maximo = rangos[lab_type]
    return round(random.uniform(minimo, maximo), 2)

def generar_procedimientos():
    for tipo, info in distribucion.items():
        creados = 0
        while creados < info['total']:
            afiliado = obtener_afiliado_aleatorio()
            cantidad = random.randint(info['min_por_afiliado'], info['max_por_afiliado'])
            for _ in range(cantidad):
                if creados >= info['total']:
                    break
                LaboratorioProcedimiento.objects.create(
                    procedure_id=f"LAB-{uuid4()}",
                    patient=afiliado,
                    cost=Decimal(generar_costos(tipo)),
                    lab_type=tipo
                )
                creados += 1
        print(f"Generados {creados} procedimientos para {tipo}")

# Ejecutar la función principal
generar_procedimientos()
