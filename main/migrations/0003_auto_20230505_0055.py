# Generated by Django 3.2.16 on 2023-05-04 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_newuser_wh'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='waiting_for',
        ),
        migrations.AddField(
            model_name='ticket',
            name='tag_to',
            field=models.CharField(blank=True, choices=[('Last Mile', 'Last Mile'), ('Fleet', 'Fleet'), ('Quality', 'Quality'), ('FulFillment', 'FulFillment'), ('Security', 'Security')], max_length=255, null=True, verbose_name='Tag To'),
        ),
    ]
