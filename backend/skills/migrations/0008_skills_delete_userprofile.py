# Generated by Django 4.2.10 on 2024-04-15 17:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('skills', '0007_alter_userprofile_skills'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skills',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acquired', models.JSONField(default=dict)),
                ('search', models.JSONField(default=dict)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
