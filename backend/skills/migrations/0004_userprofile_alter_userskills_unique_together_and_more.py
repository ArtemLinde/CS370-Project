# Generated by Django 4.2.10 on 2024-04-09 17:40

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('skills', '0003_delete_skill'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('have', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=list, size=None)),
                ('searching', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=list, size=None)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='skills_userprofile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='userskills',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='userskills',
            name='skill',
        ),
        migrations.RemoveField(
            model_name='userskills',
            name='user',
        ),
        migrations.DeleteModel(
            name='Skills',
        ),
       
    ]
