# Generated by Django 5.0.1 on 2024-01-10 07:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sub', '0007_alter_transcriberesult_redacted'),
    ]

    operations = [
        migrations.AddField(
            model_name='transcriberesult',
            name='language',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sub.langcode'),
            preserve_default=False,
        ),
    ]