# Generated by Django 4.2.15 on 2024-09-14 15:12

import SafeSurgeon.models
import cloudinary.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Surgeon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', cloudinary.models.CloudinaryField(blank=True, default='default_profile_pic', max_length=255, null=True, verbose_name='profile picture')),
                ('verification_status', models.CharField(choices=[('PENDING', 'Pending'), ('VERIFIED', 'Verified'), ('REJECTED', 'Rejected')], default='PENDING', max_length=9)),
                ('id_document', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='Id')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surgeons', to='SafeSurgeon.city')),
                ('clinic', models.ForeignKey(default=SafeSurgeon.models.Clinic.get_default_clinic, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='surgeons', to='SafeSurgeon.clinic')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surgeons', to='SafeSurgeon.country')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='surgeon', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(max_length=200)),
                ('program', models.CharField(max_length=200)),
                ('institution_country', models.CharField(default='Unknown', max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('certificate', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='certificate')),
                ('surgeon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to='SafeSurgeon.surgeon')),
            ],
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='SafeSurgeon.country'),
        ),
    ]
