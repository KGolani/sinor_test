# Generated by Django 4.0.3 on 2022-05-13 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('name', models.CharField(max_length=45)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9)),
            ],
            options={
                'db_table': 'coupon',
            },
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=120, unique=True)),
                ('transaction_id', models.CharField(blank=True, max_length=120, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=9)),
                ('success', models.BooleanField(default=False)),
                ('transaction_status', models.CharField(blank=True, max_length=220, null=True)),
                ('type', models.CharField(max_length=120)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.user')),
            ],
            options={
                'db_table': 'payment_transaction',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('paid_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('used_point', models.DecimalField(decimal_places=2, max_digits=9)),
                ('payment_method', models.CharField(max_length=45, null=True)),
                ('is_refunded', models.BooleanField(default=False)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.user')),
            ],
            options={
                'db_table': 'payments',
            },
        ),
    ]
