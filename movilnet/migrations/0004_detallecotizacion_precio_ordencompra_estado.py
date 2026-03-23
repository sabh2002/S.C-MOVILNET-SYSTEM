import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movilnet', '0003_tipoinventario_direccion'),
    ]

    operations = [
        # Agregar precio_unitario a DetalleCotizacion
        migrations.AddField(
            model_name='detallecotizacion',
            name='precio_unitario',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name='Precio Unitario',
            ),
        ),
        # Agregar estado a OrdenCompra
        migrations.AddField(
            model_name='ordencompra',
            name='estado',
            field=models.CharField(
                choices=[
                    ('pendiente', 'Pendiente'),
                    ('parcial', 'Parcialmente Recibida'),
                    ('recibida', 'Recibida'),
                    ('cancelada', 'Cancelada'),
                ],
                default='pendiente',
                max_length=20,
                verbose_name='Estado',
            ),
        ),
    ]
