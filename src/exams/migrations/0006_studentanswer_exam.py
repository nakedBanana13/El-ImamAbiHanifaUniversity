# Generated by Django 5.0.2 on 2024-03-12 04:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0005_remove_question_mark_exam_total_marks_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentanswer',
            name='exam',
            field=models.ForeignKey(default=70, on_delete=django.db.models.deletion.CASCADE, to='exams.exam'),
            preserve_default=False,
        ),
    ]
