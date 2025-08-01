# Generated by Django 5.2.4 on 2025-07-30 17:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nlp_services', '0002_analysishistory_analysis_type_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregateAnalysisHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(blank=True, db_index=True, max_length=2048, null=True)),
                ('input_fingerprint', models.CharField(db_index=True, max_length=64)),
                ('input_texts', models.JSONField()),
                ('analysis_result', models.JSONField()),
                ('analysis_source', models.CharField(max_length=20)),
                ('analysis_type', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aggregate_analysis_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Aggregate Analysis History',
                'verbose_name_plural': 'Aggregate Analysis Histories',
                'ordering': ['-timestamp'],
            },
        ),
    ]
