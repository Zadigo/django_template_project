# Generated by Django 3.1.1 on 2020-09-03 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='product_manager',
        ),
        migrations.RemoveField(
            model_name='myuserprofile',
            name='stripe_id',
        ),
        migrations.AddField(
            model_name='myuserprofile',
            name='customer_id',
            field=models.CharField(blank=True, help_text='Stripe customer ID', max_length=100, null=True),
        ),
    ]
