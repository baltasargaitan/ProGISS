import csv
import re
from django.core.management.base import BaseCommand
from gestion_datos.models import Afiliado
import os

class Command(BaseCommand):
    help = "Importa datos de afiliados desde un archivo CSV."

    def handle(self, *args, **kwargs):
        file_path = os.path.join(os.getcwd(), 'SimulacionUtilizacion.csv')

        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Archivo no encontrado en: {file_path}"))
            return

        try:
            with open(file_path, encoding='latin-1') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')

                for row in reader:
                    # Saltar filas que no sean datos válidos
                    if not row['Affiliate_ID'].startswith('AF-'):
                        continue

                    # Procesar columnas
                    medication_cost = float(re.sub(r'[^\d,]', '', row['Previous_Medication_Cost']).replace(',', '.'))
                    chronic_condition = row['Chronic_Condition'] == 'Yes'
                    enrolled_in_program = row['Enrolled_in_Program'] == 'Yes'

                    # Crear o actualizar registros
                    Afiliado.objects.update_or_create(
                        affiliate_id=row['Affiliate_ID'],
                        defaults={
                            'age': int(row['Age']),
                            'sex': row['Sex'],
                            'region': row['Region'],
                            'chronic_condition': chronic_condition,
                            'previous_consultations': int(row['Previous_Consultations']),
                            'previous_hospitalizations': int(row['Previous_Hospitalizations']),
                            'previous_medication_cost': medication_cost,
                            'enrolled_in_program': enrolled_in_program,
                            'risk_score': float(row['Risk_Score']),
                        },
                    )

            self.stdout.write(self.style.SUCCESS("Datos importados correctamente."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al importar datos: {str(e)}"))
