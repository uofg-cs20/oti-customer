# Generated by Django 3.0.3 on 2021-01-20 14:44

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
            name='Discount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_type', models.CharField(max_length=50)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=6)),
                ('discount_description', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='LatitudeLongitude',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=4, max_digits=6)),
                ('longitude', models.DecimalField(decimal_places=4, max_digits=7)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NaPTAN', models.CharField(max_length=10)),
                ('other', models.CharField(max_length=30, null=True)),
                ('other_type', models.CharField(max_length=20, null=True)),
                ('accuracy', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('lat_long', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.LatitudeLongitude')),
            ],
        ),
        migrations.CreateModel(
            name='Mode',
            fields=[
                ('id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('short_desc', models.CharField(max_length=50)),
                ('long_desc', models.CharField(max_length=8000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MonetaryValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('currency', models.CharField(max_length=3)),
                ('symbol', models.CharField(max_length=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecordID',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('reference', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('number_usages', models.CharField(max_length=3)),
                ('reference_type', models.CharField(max_length=30)),
                ('medium', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TravelClass',
            fields=[
                ('travel_class', models.CharField(max_length=50, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='UsageReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=5)),
                ('reference_type', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('included', models.BooleanField(default=True)),
                ('reference', models.CharField(max_length=20)),
                ('vehicle_type', models.CharField(max_length=20)),
                ('conditions', models.CharField(max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Concession',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='website.RecordID')),
                ('name', models.CharField(max_length=30)),
                ('valid_from_date_time', models.DateField()),
                ('valid_to_date_time', models.DateField()),
                ('conditions', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='website.RecordID')),
                ('booking_date_time', models.DateTimeField()),
                ('agent', models.CharField(max_length=100, null=True)),
                ('passenger_number', models.IntegerField(null=True)),
                ('passenger_type', models.CharField(max_length=100, null=True)),
                ('route', models.CharField(max_length=500, null=True)),
                ('travel_from_date_time', models.DateTimeField()),
                ('travel_to_date_time', models.DateTimeField()),
                ('conditions', models.CharField(max_length=500, null=True)),
                ('restrictions', models.CharField(max_length=500, null=True)),
                ('reserved_position', models.CharField(max_length=30, null=True)),
                ('service_request', models.CharField(max_length=500, null=True)),
                ('account_balance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.MonetaryValue')),
                ('concession', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='website.Concession')),
            ],
        ),
        migrations.CreateModel(
            name='UsageFromTo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('reference', models.CharField(max_length=30)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Location')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('payment_type', models.CharField(max_length=30)),
                ('payment_method', models.CharField(max_length=30)),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.MonetaryValue')),
            ],
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('homepage', models.URLField()),
                ('api_url', models.URLField()),
                ('default_language', models.CharField(default='English', max_length=40)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('active', models.BooleanField(default=True)),
                ('admin', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('modes', models.ManyToManyField(to='website.Mode')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Operator')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Usage',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='recordid', serialize=False, to='website.RecordID')),
                ('route_via_avoid', models.CharField(max_length=500, null=True)),
                ('pre_paid', models.BooleanField(null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Customer')),
                ('mode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Mode')),
                ('operator', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='website.Operator')),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.MonetaryValue')),
                ('purchase_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Purchase')),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.UsageReference')),
                ('ticket_reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Ticket')),
                ('travel_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.TravelClass')),
                ('travel_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests_created', to='website.UsageFromTo')),
                ('travel_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.UsageFromTo')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_type', models.CharField(max_length=20)),
                ('unit', models.CharField(max_length=10)),
                ('amount', models.IntegerField()),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.MonetaryValue')),
                ('usage_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Usage')),
            ],
        ),
        migrations.AddField(
            model_name='purchase',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Customer'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='location_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests_created', to='website.Location'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='location_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Location'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='mode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Mode'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='operator',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='website.Operator'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='website.Ticket'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='transaction',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='website.Transaction'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='travel_class',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.TravelClass'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Vehicle'),
        ),
        migrations.AddField(
            model_name='concession',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Customer'),
        ),
        migrations.AddField(
            model_name='concession',
            name='discount',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Discount'),
        ),
        migrations.AddField(
            model_name='concession',
            name='mode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Mode'),
        ),
        migrations.AddField(
            model_name='concession',
            name='operator',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='website.Operator'),
        ),
        migrations.AddField(
            model_name='concession',
            name='price',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.MonetaryValue'),
        ),
        migrations.AddField(
            model_name='concession',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Transaction'),
        ),
    ]
