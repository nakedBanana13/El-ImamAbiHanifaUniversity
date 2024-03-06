# Generated by Django 5.0.2 on 2024-03-05 11:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_customuser_updated'),
        ('courses', '0002_course_students'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses_created', to='accounts.instructor'),
        ),
    ]
