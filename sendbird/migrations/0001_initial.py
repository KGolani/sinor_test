# Generated by Django 4.0.3 on 2022-05-13 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('pairs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SendbirdChannel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('channel_url', models.URLField(max_length=400)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'sendbird_channels',
            },
        ),
        migrations.CreateModel(
            name='SendbirdReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reason', models.CharField(blank=True, max_length=300)),
                ('reporter_sendbird_id', models.CharField(max_length=100)),
                ('offending_sendbird_id', models.CharField(max_length=100)),
                ('sendbird_channels', models.URLField(max_length=400)),
            ],
            options={
                'db_table': 'sendbird_reports',
            },
        ),
        migrations.CreateModel(
            name='SendbirdChannelUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sendbird_channels', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sendbird.sendbirdchannel')),
                ('sendbird_guest_user', models.ForeignKey(max_length=400, on_delete=django.db.models.deletion.CASCADE, related_name='guest_user', to='users.user')),
                ('sendbird_host_user', models.ForeignKey(max_length=400, on_delete=django.db.models.deletion.CASCADE, related_name='host_user', to='users.user')),
            ],
            options={
                'db_table': 'sendbird_channel_users',
            },
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=400)),
                ('interests', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pairs.interest')),
            ],
            options={
                'db_table': 'recommendations',
            },
        ),
        migrations.CreateModel(
            name='MatchingRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sendbird_channel_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sendbird.sendbirdchanneluser')),
                ('wishlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pairs.wishlist')),
            ],
            options={
                'db_table': 'matching_rates',
            },
        ),
    ]