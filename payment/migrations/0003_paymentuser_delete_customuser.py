# Generated by Django 4.2.7 on 2023-11-26 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_customuser_uuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(editable=False, unique=True)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]
