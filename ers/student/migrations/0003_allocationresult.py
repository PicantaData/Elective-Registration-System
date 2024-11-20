# Generated by Django 4.2 on 2024-10-29 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_studentuser_semester_studentrequirements_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllocationResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=15)),
                ('priority', models.IntegerField()),
                ('cum_priority', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='student.studentuser')),
            ],
        ),
    ]