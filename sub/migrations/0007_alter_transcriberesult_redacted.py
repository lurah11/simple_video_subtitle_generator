# Generated by Django 5.0.1 on 2024-01-10 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sub', '0006_alter_transcriberesult_redacted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcriberesult',
            name='redacted',
            field=models.BooleanField(default=False),
        ),
    ]
