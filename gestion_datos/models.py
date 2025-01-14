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

    def __str__(self):
        return f"{self.affiliate_id} - {self.region}"
