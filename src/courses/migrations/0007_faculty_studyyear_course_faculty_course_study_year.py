# Generated by Django 5.0.2 on 2024-02-23 20:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_alter_video_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudyYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(choices=[('1', 'First Year'), ('2', 'Second Year')], max_length=1)),
                ('semester', models.CharField(choices=[('1', 'First Semester'), ('2', 'Second Semester')], max_length=1)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='faculty',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='courses.faculty'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='study_year',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='courses.studyyear'),
            preserve_default=False,
        ),
    ]
