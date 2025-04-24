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

# Cantidades fijas de estudios a asignar
cantidad_estudios = {
    'RML': 16,   # RMN Lumbar (>20 años)
    'RTX': 15,   # Rx Tórax (>20 años)
    'EM': 29,    # Eco Mamaria (mujeres >40 años)
    'ECG': 66,   # ECG (todas las edades)
    'TCC': 15,   # TAC Cráneo (todas las edades)
}

# Función para seleccionar afiliados elegibles
def seleccionar_afiliados(filtro, cantidad):
    afiliados = list(Afiliado.objects.filter(**filtro))
    return random.sample(afiliados, min(len(afiliados), cantidad))

# Generar estudios con cantidades fijas
def generar_estudios_controlados():
    criterios = {
        'RML': {'age__gt': 20},                  # RMN Lumbar (>20 años)
        'RTX': {'age__gt': 20},                  # Rx Tórax (>20 años)
        'EM': {'age__gt': 40, 'sex': 'Femenino'},# Eco Mamaria (>40 años, mujeres)
        'ECG': {},                               # ECG (todas las edades)
        'TCC': {},                               # TAC Cráneo (todas las edades)
    }

    for study_type, cantidad in cantidad_estudios.items():
        afiliados_seleccionados = seleccionar_afiliados(criterios[study_type], cantidad)
        
        for afiliado in afiliados_seleccionados:
            # Generar fecha aleatoria dentro de los últimos 90 días
            requested_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            # Estado aleatorio
            status = random.choice(['Completado', 'Pendiente', 'Rechazado'])
            
            # Costo aleatorio
            cost = round(random.uniform(2000, 12000), 2)
            
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

    print(f"Se han asignado los estudios según las cantidades predefinidas.")

# Ejecutar la función
generar_estudios_controlados()
