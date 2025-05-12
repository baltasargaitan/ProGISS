import os
from uuid import uuid4
import django
import random
from datetime import datetime, timedelta

# Establecer la variable de entorno DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_giss.settings')

# Configurar Django
django.setup()

# Importar modelos después de configurar Django
from gestion_datos.models import EstudioProcedimiento, Afiliado

# Cantidades totales de estudios por tipo (según la tabla proporcionada)
cantidad_estudios = {
    'Radiografías': 3177,
    'Ecografías': 3194,
    'Mamografías': 667,
    'Tomografías': 251,
    'Resonancias': 298,
}

# Criterios de selección por tipo de estudio
criterios = {
    'Radiografías': {},  # Todas las edades
    'Ecografías': {},    # Todas las edades
    'Mamografías': {'age__gt': 40, 'sex': 'Femenino'},  # Mujeres mayores de 40 años
    'Tomografías': {},   # Todas las edades
    'Resonancias': {},   # Todas las edades
}

# Generar estudios distribuidos proporcionalmente
def generar_estudios_distribuidos():
    estudios_no_asignados = 0  # Contador para estudios no asignados

    for study_type, total_estudios in cantidad_estudios.items():
        afiliados_seleccionados = list(Afiliado.objects.filter(**criterios[study_type]))
        
        # Asegurarse de que haya suficientes afiliados para asignar estudios
        if not afiliados_seleccionados:
            print(f"No hay afiliados elegibles para {study_type}. Se omitirán {total_estudios} estudios.")
            estudios_no_asignados += total_estudios
            continue

        for _ in range(total_estudios):
            # Seleccionar un afiliado aleatorio (puede repetirse)
            afiliado = random.choice(afiliados_seleccionados)
            
            # Generar fecha aleatoria dentro de los últimos 90 días
            requested_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            # Estado aleatorio
            status = random.choice(['Completado', 'Pendiente', 'Rechazado'])
            
            # Costo aleatorio
            cost = round(random.uniform(15000, 120000), 2)
            
            # Cumplimiento con la directriz aleatorio
            compliance = random.choice([True, False])
            
            # Crear el estudio
            EstudioProcedimiento.objects.create(
                procedure_id=f"PROC-{uuid4()}",
                patient=afiliado,
                study_type=study_type,
                requested_date=requested_date,
                status=status,
                cost=cost,
                compliance_with_guideline=compliance
            )

    print(f"Se han distribuido los {sum(cantidad_estudios.values()) - estudios_no_asignados} estudios entre los afiliados.")
    print(f"Estudios no asignados: {estudios_no_asignados}")
# Ejecutar la función
generar_estudios_distribuidos()