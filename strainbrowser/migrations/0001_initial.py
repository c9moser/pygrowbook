# Generated by Django 4.0.6 on 2022-11-19 13:43

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Breeder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=64, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')])),
                ('name', models.CharField(max_length=128, unique=True)),
                ('seedfinder', models.CharField(blank=True, default='', max_length=512, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])])),
                ('homepage', models.CharField(blank=True, default='', max_length=512, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])])),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='breeder_added_by', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='breeder_edited_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('strainbrowser.operator', 'Strainbrowser operator'), ('strainbrowser.breeder.add', 'Allowed to add breeders'), ('strainbrowser.breeder.edit', 'Allowed to edit all breeders'), ('strainbrowser.breeder.delete', 'Allowed to delete breeders')],
            },
        ),
        migrations.CreateModel(
            name='Strain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=64, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')])),
                ('name', models.CharField(max_length=256)),
                ('seedfinder', models.CharField(blank=True, default='', max_length=512, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])])),
                ('homepage', models.CharField(blank=True, default='', max_length=512, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])])),
                ('info', models.TextField(blank=True, default='')),
                ('description', models.TextField(blank=True, default='')),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.RESTRICT, related_name='strain_added_by', to=settings.AUTH_USER_MODEL)),
                ('breeder', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.RESTRICT, to='strainbrowser.breeder')),
                ('edited_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.RESTRICT, related_name='strain_edited_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('strainbrowser.strain.translate', 'Allowed to translate strains'), ('strainbrowser.strain.add', 'Allowed to add strains'), ('strainbrowser.strain.edit', 'Allowed to edit strains'), ('strainbrowser.strain.delete', 'Allowed to delete strains')],
            },
        ),
        migrations.CreateModel(
            name='StrainTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('homepage', models.CharField(blank=True, default='', max_length=512, null=True, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])])),
                ('seedfinder', models.CharField(blank=True, default='', max_length=512, null=True, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])])),
                ('info', models.TextField(default='')),
                ('description', models.TextField(default='')),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='strain_translation_added_by', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='strain_translation_edited_by', to=settings.AUTH_USER_MODEL)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='main.language')),
                ('strain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strainbrowser.strain')),
            ],
        ),
        migrations.CreateModel(
            name='StrainBackup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=256)),
                ('homepage', models.CharField(blank=True, max_length=512, null=True, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])])),
                ('seedfinder', models.CharField(blank=True, max_length=512, null=True, validators=[django.core.validators.URLValidator(schemes=['http', 'https'])])),
                ('info', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('edited_on', models.DateTimeField(editable=False)),
                ('backup_on', models.DateTimeField(auto_now=True)),
                ('backup_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='strain_backup_by', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='strain_backup_edited_by', to=settings.AUTH_USER_MODEL)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='language', to='main.language')),
                ('strain', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='strainbrowser.strain')),
                ('strain_translation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='strainbrowser.straintranslation')),
            ],
        ),
    ]