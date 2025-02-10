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

# Listado de estudios a usar
study_types = ['RML', 'RTX', 'EM', 'ECGR', 'TCC', 'PSA']

# Generar estudios para los afiliados
def generar_estudios_por_afiliado():
    afiliados = Afiliado.objects.all()
    for afiliado in afiliados:
        # Asignar un número de estudios aleatorio, por ejemplo, entre 0 y 3
        num_estudios = random.randint(0, 3)  # Ajusta según estadísticas reales
        for _ in range(num_estudios):
            # Seleccionar un tipo de estudio aleatorio
            study_type = random.choice(study_types)

            # Si el estudio es "EM" (Ecografía Mamaria), asegurarse de que el afiliado sea mujer
            if study_type == 'EM' and afiliado.sex != 'Femenino':
                # Si el afiliado no es mujer, asignar un estudio diferente
                study_type = random.choice([s for s in study_types if s != 'EM'])

            # Fecha aleatoria dentro de un rango de fechas (últimos 90 días)
            random_days = random.randint(1, 90)
            requested_date = datetime.now() - timedelta(days=random_days)

            # Estado aleatorio
            status = random.choice(['Completado', 'Pendiente', 'Rechazado'])

            # Costo aleatorio
            cost = round(random.uniform(2000, 12000), 2)

            # Cumplimiento con la directriz aleatoriamente
            compliance = random.choice([True, False])

            # Crear un nuevo procedimiento para este afiliado con el ID de afiliado (no UUID)
            EstudioProcedimiento.objects.create(
                procedure_id=f"PROC-{uuid4()}",  # UUID como procedure_id único
                patient=afiliado,  # Relacionamos con el paciente (afiliado)
                study_type=study_type,
                requested_date=requested_date,
                status=status,
                cost=cost,
                compliance_with_guideline=compliance
            )

    print(f"Se generaron estudios para {len(afiliados)} afiliados.")

# Llamar a la función para generar los estudios
generar_estudios_por_afiliado()
