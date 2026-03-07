from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movilnet', '0002_tipoinventario_cotizacion_detallecotizacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipoinventario',
            name='direccion',
            field=models.CharField(
                choices=[('ENTRADA', 'Entrada (suma stock)'), ('SALIDA', 'Salida (resta stock)')],
                default='ENTRADA',
                max_length=10,
                verbose_name='Dirección',
                help_text='ENTRADA suma unidades al stock. SALIDA las resta.'
            ),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='tipoinventario',
            options={
                'ordering': ['direccion', 'tipo_movimiento'],
                'verbose_name': 'Tipo de Inventario',
                'verbose_name_plural': 'Tipos de Inventario',
            },
        ),
        migrations.AlterField(
            model_name='tipoinventario',
            name='tipo_movimiento',
            field=models.CharField(max_length=50, verbose_name='Nombre del Tipo'),
        ),
        migrations.AlterField(
            model_name='tipoinventario',
            name='categoria_movimiento',
            field=models.CharField(max_length=50, verbose_name='Descripción / Categoría'),
        ),
        migrations.AddConstraint(
            model_name='tipoinventario',
            constraint=models.UniqueConstraint(
                fields=['tipo_movimiento', 'direccion'],
                name='unique_tipo_direccion'
            ),
        ),
    ]
