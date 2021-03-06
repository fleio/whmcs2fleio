# Generated by Django 2.1.2 on 2018-11-29 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whmcsync', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tblpricing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=14)),
                ('currency', models.IntegerField()),
                ('relid', models.IntegerField()),
                ('msetupfee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('qsetupfee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ssetupfee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('asetupfee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('bsetupfee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tsetupfee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('monthly', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quarterly', models.DecimalField(decimal_places=2, max_digits=10)),
                ('semiannually', models.DecimalField(decimal_places=2, max_digits=10)),
                ('annually', models.DecimalField(decimal_places=2, max_digits=10)),
                ('biennially', models.DecimalField(decimal_places=2, max_digits=10)),
                ('triennially', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'tblpricing',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tblservergroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('filltype', models.IntegerField()),
            ],
            options={
                'db_table': 'tblservergroups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tblservergroupsrel',
            fields=[
                ('groupid', models.IntegerField()),
                ('serverid', models.IntegerField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'tblservergroupsrel',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tblservers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('ipaddress', models.TextField()),
                ('assignedips', models.TextField()),
                ('hostname', models.TextField()),
                ('monthlycost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('noc', models.TextField()),
                ('statusaddress', models.TextField()),
                ('nameserver1', models.TextField()),
                ('nameserver1ip', models.TextField()),
                ('nameserver2', models.TextField()),
                ('nameserver2ip', models.TextField()),
                ('nameserver3', models.TextField()),
                ('nameserver3ip', models.TextField()),
                ('nameserver4', models.TextField()),
                ('nameserver4ip', models.TextField()),
                ('nameserver5', models.TextField()),
                ('nameserver5ip', models.TextField()),
                ('maxaccounts', models.IntegerField()),
                ('type', models.TextField()),
                ('username', models.TextField()),
                ('password', models.TextField()),
                ('accesshash', models.TextField()),
                ('secure', models.TextField()),
                ('port', models.IntegerField(blank=True, null=True)),
                ('active', models.IntegerField()),
                ('disabled', models.IntegerField()),
            ],
            options={
                'db_table': 'tblservers',
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='syncedaccount',
            name='whmcs_uuid',
            field=models.CharField(db_index=True, max_length=64),
        ),
    ]
