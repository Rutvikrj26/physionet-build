# Generated by Django 3.1.14 on 2022-12-09 18:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0063_auto_20220528_2248'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activeproject',
            options={
                'default_permissions': ('change',),
                'permissions': [
                    ('can_assign_editor', 'Can assign editor'), ('can_edit_activeprojects', 'Can edit ActiveProjects')
                ]
            },
        ),
    ]
