# Generated by Django 5.0.2 on 2024-03-05 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_customuser_updated'),
        ('courses', '0006_alter_file_owner_alter_image_owner_alter_text_owner_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(related_name='courses_joined', to='accounts.student'),
        ),
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.FileField(upload_to=''),
        ),
    ]