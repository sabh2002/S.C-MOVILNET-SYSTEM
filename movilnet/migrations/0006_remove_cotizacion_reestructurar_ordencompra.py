from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movilnet', '0005_alter_tipoinventario_categoria_movimiento_and_more'),
    ]

    operations = [
        # 1. Eliminar DetalleOrdenCompra (depende de OrdenCompra y Cotizacion via cotizacion.detalles)
        migrations.DeleteModel(name='DetalleOrdenCompra'),

        # 2. Eliminar OrdenCompra (depende de Cotizacion)
        migrations.DeleteModel(name='OrdenCompra'),

        # 3. Eliminar DetalleCotizacion (depende de Cotizacion)
        migrations.DeleteModel(name='DetalleCotizacion'),

        # 4. Eliminar Cotizacion
        migrations.DeleteModel(name='Cotizacion'),

        # 5. Crear nuevo OrdenCompra
        migrations.CreateModel(
            name='OrdenCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(
                    choices=[('orden', 'Orden de Compra'), ('compra', 'Compra')],
                    default='orden',
                    max_length=10,
                    verbose_name='Tipo'
                )),
                ('numero_orden', models.CharField(max_length=50, unique=True, verbose_name='Número')),
                ('fecha_orden', models.DateField(verbose_name='Fecha')),
                ('total', models.DecimalField(
                    decimal_places=2, default=0, max_digits=12,
                    validators=[django.core.validators.MinValueValidator(0)],
                    verbose_name='Total'
                )),
                ('observaciones', models.TextField(blank=True, null=True, verbose_name='Observaciones')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')),
                ('proveedor', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='ordenes_compra',
                    to='movilnet.proveedor',
                    verbose_name='Proveedor'
                )),
            ],
            options={
                'verbose_name': 'Orden de Compra',
                'verbose_name_plural': 'Órdenes de Compra',
                'ordering': ['-fecha_orden'],
            },
        ),

        # 6. Crear nuevo DetalleOrdenCompra
        migrations.CreateModel(
            name='DetalleOrdenCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(1)],
                    verbose_name='Cantidad'
                )),
                ('precio_unitario', models.DecimalField(
                    decimal_places=2, default=0, max_digits=10,
                    validators=[django.core.validators.MinValueValidator(0)],
                    verbose_name='Precio Unitario'
                )),
                ('orden_compra', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='detalles',
                    to='movilnet.ordencompra',
                    verbose_name='Orden'
                )),
                ('producto', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='detalles_orden_compra',
                    to='movilnet.producto',
                    verbose_name='Producto'
                )),
            ],
            options={
                'verbose_name': 'Detalle de Orden',
                'verbose_name_plural': 'Detalles de Orden',
            },
        ),
    ]
