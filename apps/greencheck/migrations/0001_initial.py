# Generated by Django 2.2.6 on 2019-10-30 10:52

from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models
import django_unixdatetimefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_add_django_user_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Greencheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', django_unixdatetimefield.fields.UnixDateTimeField(db_column='datum')),
                ('green', django_mysql.models.EnumField(choices=[('yes', 'yes'), ('no', 'no'), ('old', 'old')])),
                ('ip', models.IntegerField()),
                ('tld', models.CharField(max_length=64)),
                ('type', django_mysql.models.EnumField(choices=[('as', 'asn'), ('ip', 'ip'), ('none', 'none'), ('url', 'url'), ('whois', 'whois')])),
                ('url', models.CharField(max_length=255)),
                ('hostingprovider', models.ForeignKey(db_column='id_hp', on_delete=django.db.models.deletion.CASCADE, to='accounts.Hostingprovider')),
            ],
            options={
                'db_table': 'greencheck',
            },
        ),
        migrations.CreateModel(
            name='GreencheckLinked',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='GreencheckStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked_through', django_mysql.models.EnumField(choices=[('admin', 'admin'), ('api', 'api'), ('apisearch', 'apisearch'), ('bots', 'bots'), ('test', 'test'), ('website', 'website')])),
                ('count', models.IntegerField()),
                ('ips', models.IntegerField()),
            ],
            options={
                'db_table': 'greencheck_stats',
            },
        ),
        migrations.CreateModel(
            name='GreencheckStatsTotal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked_through', django_mysql.models.EnumField(choices=[('admin', 'admin'), ('api', 'api'), ('apisearch', 'apisearch'), ('bots', 'bots'), ('test', 'test'), ('website', 'website')])),
                ('count', models.IntegerField()),
                ('ips', models.IntegerField()),
            ],
            options={
                'db_table': 'greencheck_stats_total',
            },
        ),
        migrations.CreateModel(
            name='GreencheckWeeklyStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checks_green', models.IntegerField()),
                ('checks_grey', models.IntegerField()),
                ('checks_perc', models.FloatField()),
                ('checks_total', models.IntegerField()),
                ('monday', models.DateField(db_column='maandag')),
                ('url_green', models.IntegerField()),
                ('url_grey', models.IntegerField()),
                ('url_perc', models.FloatField()),
                ('week', models.IntegerField()),
                ('year', models.PositiveSmallIntegerField()),
            ],
            options={
                'db_table': 'greencheck_weekly',
            },
        ),
        migrations.CreateModel(
            name='GreenList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_checked', django_unixdatetimefield.fields.UnixDateTimeField()),
                ('name', models.CharField(db_column='naam', max_length=255)),
                ('type', django_mysql.models.EnumField(choices=[('as', 'asn'), ('ip', 'ip'), ('none', 'none'), ('url', 'url'), ('whois', 'whois')])),
                ('url', models.CharField(max_length=255)),
                ('website', models.CharField(max_length=255)),
                ('greencheck', models.ForeignKey(db_column='id_greencheck', on_delete=django.db.models.deletion.CASCADE, to='greencheck.Greencheck')),
                ('hostingprovider', models.ForeignKey(db_column='id_hp', on_delete=django.db.models.deletion.CASCADE, to='accounts.Hostingprovider')),
            ],
            options={
                'db_table': 'greenlist',
            },
        ),
        migrations.CreateModel(
            name='GreencheckIpApprove',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.TextField()),
                ('idorig', models.IntegerField()),
                ('ip_end', models.IntegerField(db_column='ip_eind')),
                ('ip_start', models.IntegerField()),
                ('status', models.TextField()),
                ('hostingprovider', models.ForeignKey(db_column='id_hp', null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Hostingprovider')),
            ],
            options={
                'db_table': 'greencheck_ip_approve',
            },
        ),
        migrations.CreateModel(
            name='GreencheckIp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(null=True)),
                ('ip_end', models.IntegerField(db_column='ip_eind')),
                ('ip_start', models.IntegerField()),
                ('hostingprovider', models.ForeignKey(db_column='id_hp', on_delete=django.db.models.deletion.CASCADE, to='accounts.Hostingprovider')),
            ],
            options={
                'db_table': 'greencheck_ip',
            },
        ),
        migrations.AddIndex(
            model_name='greenlist',
            index=models.Index(fields=['url'], name='greenlist_url_6fdd24_idx'),
        ),
        migrations.AddIndex(
            model_name='greencheckip',
            index=models.Index(fields=['ip_end'], name='greencheck__ip_eind_f65bcc_idx'),
        ),
        migrations.AddIndex(
            model_name='greencheckip',
            index=models.Index(fields=['ip_start'], name='greencheck__ip_star_fb1b28_idx'),
        ),
        migrations.AddIndex(
            model_name='greencheckip',
            index=models.Index(fields=['active'], name='greencheck__active_32fc31_idx'),
        ),
    ]
