# Generated by Django 5.1.6 on 2025-05-16 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_reviewmodel_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='productmodel',
            name='product_unit',
            field=models.CharField(choices=[('kg', 'Kilogram'), ('g', 'Gram'), ('litre', 'Litre'), ('ml', 'Millilitre'), ('piece', 'Piece'), ('pack', 'Pack')], default='piece', max_length=10),
        ),
    ]
