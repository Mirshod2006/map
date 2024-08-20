from django.db import models
from django.utils import timezone

tz = timezone.get_default_timezone()

class Admin(models.Model):
    a_name = models.CharField(max_length=15, verbose_name='User name')
    a_word = models.CharField(max_length=15, verbose_name='Password')

class Huawei(models.Model):
    u_name = models.CharField(max_length=15, verbose_name='User name')
    p_word = models.CharField(max_length=15, verbose_name='Password')
    sub_domain = models.CharField(max_length=10, verbose_name='Subdomain')
    
    class Meta:
        app_label = 'mapproject'
        
class Solax(models.Model):
    #'token, Sn, lat, lon, name
    token = models.CharField(max_length=35, verbose_name='Token')
    sn = models.CharField(max_length=35, verbose_name='SN')
    lat = models.FloatField(max_length=35, verbose_name='Lat')
    lon = models.FloatField(max_length=35, verbose_name='Lon')
    name = models.CharField(max_length=35, verbose_name='Stantion name')
    inverterPower = models.FloatField(max_length=35, default="30 kW", verbose_name='inverterPower')
    
    class Meta:
        app_label = 'mapproject'
        

class Data(models.Model):
    lat = models.CharField(max_length=20, verbose_name='Latitude')
    lon = models.CharField(max_length=20, verbose_name='Longitude')
    inverterPower = models.FloatField(max_length=5, verbose_name='Inverter power')
    gridConnectedTime = models.DateTimeField(verbose_name='Grid connected time')
    abs_val = models.FloatField(max_length=10, verbose_name='Current power')
    use = models.FloatField(max_length=10, verbose_name='Daily energy')
    pv = models.FloatField(max_length=10, verbose_name='Year energy')
    name = models.CharField(max_length=20, verbose_name='Name search')
    regions = models.CharField(max_length=20, verbose_name='Regions')
    adress = models.CharField(max_length=20, verbose_name='Adress')
    get_id = models.CharField(max_length=35, verbose_name='Meteo Id', default="None")
    
    
    def __str__(self):
        return self.lat  # Replace field1 with an appropriate field for representation
    
    class Meta:
        app_label = 'mapproject'

class MeteoData(models.Model):
    meteo_id = models.CharField(max_length=35, verbose_name='ID')
    lat = models.FloatField(max_length=35, verbose_name='Lat')
    lon = models.FloatField(max_length=35, verbose_name='Lon')
    name = models.CharField(max_length=35, verbose_name='Stantion name')
    
    class Meta:
        app_label = 'mapproject'

class OpenMeteo(models.Model):
    time = models.DateTimeField(verbose_name='Time')
    shortwave_radiation_instant = models.FloatField(max_length=35, verbose_name='Shortwave radiation instant')
    temperature_2m = models.FloatField(max_length=35, verbose_name='Temperature 2m')
    windspeed_10m = models.FloatField(max_length=35, verbose_name='Windspeed 10m')
    relativehumidity_2m = models.FloatField(max_length=35, verbose_name='Relativehumidity 2m', default='None')

    def __str__(self):
        return self.time
    
class Real(models.Model):
    time = models.DateTimeField(verbose_name='Time')
    meteo_id = models.CharField(max_length=35, verbose_name='Meteo Id')
    temp = models.FloatField(max_length=35, verbose_name='Temperature', default=0)
    t_air_min = models.FloatField(max_length=35, verbose_name='Min temperature', default=0)
    t_air_max = models.FloatField(max_length=35, verbose_name='Max temperature', default=0)
    rel_hum = models.FloatField(max_length=35, verbose_name='Relativehumidity 2m', default=0)
    windspeed = models.FloatField(max_length=35, verbose_name='Windspeed 10m', default=0)
    winddir = models.FloatField(max_length=35, verbose_name='winddir', default=0)
    solarradiation = models.FloatField(max_length=35, verbose_name='Shortwave radiation instant', default=0.0, null=True, blank=True)

    def __str__(self):
        return self.time
    
class GetData(models.Model):
    time = models.DateTimeField(verbose_name='Time')
    get_id = models.CharField(max_length=35, verbose_name='Meteo Id')
    real_power = models.FloatField(max_length=35, verbose_name='Relativehumidity 2m', default=0)
    abs_power = models.FloatField(max_length=35, verbose_name='Windspeed 10m', default=0)
    year_power = models.FloatField(max_length=35, verbose_name='Windspeed 10m', default=0)

    def __str__(self):
        return self.time   