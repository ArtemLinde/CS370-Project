# Generated by Django 4.2.10 on 2024-04-08 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("friendsSystem", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="friendrequest",
            name="friendRequest_id",
            field=models.CharField(default="null", max_length=255),
        ),
    ]
