from django.db import models

class Afiliado(models.Model):
    affiliate_id = models.CharField(max_length=20, unique=True)
    age = models.IntegerField()
    sex = models.CharField(max_length=10)
    region = models.CharField(max_length=50)
    chronic_condition = models.BooleanField()
    previous_consultations = models.IntegerField()
    previous_hospitalizations = models.IntegerField()
    previous_medication_cost = models.DecimalField(max_digits=10, decimal_places=2)
    enrolled_in_program = models.BooleanField()
    risk_score = models.FloatField()
        
    # Nueva columna plan
    plan = models.CharField(max_length=50, default="Básico")

    def __str__(self):
        return f"{self.affiliate_id} - {self.plan}" 


'------------------------------------------------------------'

class EstudioProcedimiento(models.Model):
    
    study_type = models.CharField(max_length=50, default="No especificado")
    procedure_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Afiliado, on_delete=models.CASCADE, related_name="procedures")
    procedure_id = models.CharField(max_length=30)
    requested_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pendiente')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    compliance_with_guideline = models.BooleanField()

    def __str__(self):
        return f"Estudio {self.study_type} - {self.patient.affiliate_id}"


class LaboratorioProcedimiento(models.Model):
    procedure_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Afiliado, on_delete=models.CASCADE, related_name="labprocedures")
    cost = models.DecimalField(max_digits=10, decimal_places=2)  
    lab_type = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.lab_type}"



'------------------------------------------------------------'
class Medico(models.Model):
    doctor_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    specialty = models.CharField(max_length=100)
    hospital_affiliation = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialty}"
    

'------------------------------------------------------------'
class Auditoria(models.Model):
    audit_id = models.CharField(max_length=20, unique=True)
    procedure = models.ForeignKey(EstudioProcedimiento, on_delete=models.CASCADE, related_name="audits")
    auditor = models.CharField(max_length=50)
    audit_date = models.DateTimeField(auto_now_add=True)
    audit_result = models.TextField()
    recommendation = models.TextField()
    
    def __str__(self):
        return f"Auditoría {self.audit_id} - Estudio {self.procedure.study_type}"
    

'------------------------------------------------------------'
class CostosEstadisticas(models.Model):
    affiliate = models.ForeignKey(Afiliado, on_delete=models.CASCADE, related_name="cost_statistics")
    total_medication_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_procedure_cost = models.DecimalField(max_digits=10, decimal_places=2)
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Estadísticas de costos - {self.affiliate.affiliate_id}"

