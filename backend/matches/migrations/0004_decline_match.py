# Generated by Django 4.2.2 on 2024-04-30 03:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('matches', '0003_declinedmatch'),
    ]

    operations = [
        migrations.CreateModel(
            name='decline_match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('declined_at', models.DateTimeField(auto_now_add=True)),
                ('declined_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='declined_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='declined_matches', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'declined_user')},
            },
        ),
    ]