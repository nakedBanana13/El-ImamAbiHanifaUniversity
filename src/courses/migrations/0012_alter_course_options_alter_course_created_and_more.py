# Generated by Django 5.0.2 on 2024-03-14 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_customuser_is_active'),
        ('courses', '0011_module_is_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['-created'], 'verbose_name': 'الدورة', 'verbose_name_plural': 'الدورات'},
        ),
        migrations.AlterField(
            model_name='course',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء'),
        ),
        migrations.AlterField(
            model_name='course',
            name='faculty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='courses.faculty', verbose_name='الكلية'),
        ),
        migrations.AlterField(
            model_name='course',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='نشطة'),
        ),
        migrations.AlterField(
            model_name='course',
            name='overview',
            field=models.TextField(verbose_name='نبذة عن الدورة'),
        ),
        migrations.AlterField(
            model_name='course',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses_created', to='accounts.instructor', verbose_name='المدرس'),
        ),
        migrations.AlterField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='courses_joined', to='accounts.student', verbose_name='الطلاب'),
        ),
        migrations.AlterField(
            model_name='course',
            name='study_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='courses.studyyear', verbose_name='العام الدراسي'),
        ),
        migrations.AlterField(
            model_name='course',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='courses.subject', verbose_name='المادة'),
        ),
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.CharField(max_length=200, verbose_name='العنوان'),
        ),
    ]