# Generated by Django 5.0.2 on 2024-03-21 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_alter_student_country_born'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='language',
            field=models.CharField(choices=[('العربية', 'العربية'), ('الإنجليزية', 'الإنجليزية'), ('الفرنسية', 'الفرنسية'), ('الفارسية', 'الفارسية'), ('آردو', 'آردو'), ('الأندونيسية', 'الأندونيسية'), ('الباكستانية', 'الباكستانية'), ('غير ذلك', 'غير ذلك')], max_length=50, verbose_name='اللغة الأم'),
        ),
        migrations.DeleteModel(
            name='Document',
        ),
    ]
