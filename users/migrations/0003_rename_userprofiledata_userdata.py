# Generated by Django 3.2.5 on 2021-07-06 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofiledata'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserProfileData',
            new_name='UserData',
        ),
    ]
