# Generated by Django 3.2.16 on 2023-06-05 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_ticket_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='warehouse',
            field=models.CharField(blank=True, choices=[('Mostorod', 'Mostorod'), ('Basatin', 'Basatin'), ('Haram', 'Haram'), ('Basous', 'Basous'), ('All', 'All')], max_length=255, null=True, verbose_name='Warehouse'),
        ),
    ]
