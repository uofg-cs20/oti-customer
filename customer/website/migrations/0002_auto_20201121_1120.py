# Generated by Django 3.0.3 on 2020-11-21 11:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='concession',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='website.Concession'),
        ),
    ]
