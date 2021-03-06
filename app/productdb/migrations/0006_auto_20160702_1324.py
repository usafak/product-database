# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-02 11:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productdb', '0005_auto_20160608_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobfile',
            name='file',
            field=models.FileField(upload_to='data'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, default='', help_text='description', null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=models.TextField(blank=True, default='', help_text='unformatted tag field', null=True, verbose_name='Tags'),
        ),
    ]
