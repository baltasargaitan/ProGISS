import os
import django

# Establecer la variable de entorno DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro_giss.settings')

# Configurar Django
django.setup()

# Importar modelos después de configurar Django
from gestion_datos.models import EstudioProcedimiento, Afiliado
import random
from datetime import datetime, timedelta

# Listado de estudios a usar
study_types = ['RML', 'RTX', 'EM', 'ECGR', 'TCC', 'PSA']

# Crear 50 nuevos procedimientos
for i in range(50):
    # Seleccionamos un afiliado aleatorio para asignar el procedimiento
    afiliado = Afiliado.objects.all().order_by('?').first()

    if afiliado:  # Validar que haya afiliados en la base de datos
        # Seleccionamos un estudio aleatorio
        study_type = random.choice(study_types)

        # Fecha aleatoria dentro de un rango de fechas (últimos 30 días)
        random_days = random.randint(1, 30)
        requested_date = datetime.now() - timedelta(days=random_days)

        # Estado aleatorio
        status = random.choice(['Completado', 'Pendiente', 'Rechazado'])

        # Costo aleatorio
        cost = round(random.uniform(2000, 12000), 2)

        # Cumple con la directriz aleatoriamente
        compliance = random.choice([True, False])

        # Crear una nueva instancia de EstudioProcedimiento
        EstudioProcedimiento.objects.create(
            procedure_id=f"PROC-{i+50}",  # Procedimiento con ID incremental
            patient=afiliado,  # Ajustar según el campo real en tu modelo
            study_type=study_type,
            requested_date=requested_date,
            status=status,
            cost=cost,
            compliance_with_guideline=compliance
        )
    else:
        print("No se encontraron afiliados en la base de datos. Procedimientos no creados.")
        break

print("50 nuevos procedimientos creados.")
