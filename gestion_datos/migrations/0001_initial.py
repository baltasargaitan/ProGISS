# Generated by Django 5.1.4 on 2025-01-13 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Afiliado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('affiliate_id', models.CharField(max_length=20, unique=True)),
                ('age', models.IntegerField()),
                ('sex', models.CharField(max_length=10)),
                ('region', models.CharField(max_length=50)),
                ('chronic_condition', models.BooleanField()),
                ('previous_consultations', models.IntegerField()),
                ('previous_hospitalizations', models.IntegerField()),
                ('previous_medication_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('enrolled_in_program', models.BooleanField()),
                ('risk_score', models.FloatField()),
            ],
        ),
    ]