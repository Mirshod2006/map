from django.shortcuts import render, redirect
import ansi
import urllib3
import schedule
from datetime import datetime
# from folium.plugins import MarkerCluster
import pandas as pd
from django.http import JsonResponse
import json
from django.http import HttpResponse
# from fusion_solar_py.client import FusionSolarClient
import numpy as np
import requests
import datetime
from .client import FusionSolarClient
from geopy.geocoders import Nominatim
from mapproject.models import Solax
from mapproject.models import MeteoData
from mapproject.models import Huawei
from mapproject.models import Data
from mapproject.models import OpenMeteo
from mapproject.models import Real
from mapproject.models import GetData
from django.db.models import F
from datetime import datetime
from django.utils.dateparse import parse_datetime
from django.core.serializers import serialize
from django.shortcuts import render
import pytz
import warnings
import mpld3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.views.decorators.csrf import csrf_exempt
from math import radians, sin, cos, sqrt, atan2
import time
from django.test import Client



warnings.filterwarnings("ignore", category=RuntimeWarning, module="django.db.models.fields")

def index(request):
    
    return render(request, 'index.html')

    

def find_closest_solar_id(solarID22, meteoData_one2):

    closest_station = None
    min_distance = float('inf')

    meteo_id = meteoData_one2['meteo_id'].values
    lat_meteo = radians(float(meteoData_one2['lat'].values[0]))  # Convert to radians
    lon_meteo = radians(float(meteoData_one2['lon'].values[0]))  # Convert to radians

    for i in solarID22['meteo_id'].unique():
        newsolar = solarID22[solarID22['meteo_id'] == i]
        lat_solar = radians(float(newsolar['lat'].values[0]))  # Convert to radians
        lon_solar = radians(float(newsolar['lon'].values[0]))  # Convert to radians

        R = 6371.0  # Earth radius in kilometers

        # Calculate the differences in coordinates
        dlon = lon_solar - lon_meteo
        dlat = lat_solar - lat_meteo

        # Apply Haversine formula
        a = sin(dlat / 2)**2 + cos(lat_meteo) * cos(lat_solar) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Calculate distance between points
        distance = R * c

        if distance < min_distance:
            min_distance = distance
            closest_station = i


    return closest_station, min_distance


def OpenMeteos(lat, lon):
    OpenMeteo.objects.all().delete()
    api_url = "https://api.open-meteo.com/v1/dwd-icon"
    params = {
        'latitude': lat,
        'longitude': lon,
        'hourly': 'temperature_2m,relativehumidity_2m,windspeed_10m,winddirection_10m,shortwave_radiation_instant',
        'timezone': 'Asia/Tashkent'
    }
    response = requests.get(api_url, params=params)
    print(lat, lon, "fggghgh")
    if response.status_code == 200:
        json_data = response.json()
        df = pd.DataFrame(json_data['hourly'])
        df['time'] = pd.to_datetime(df['time'])

        # Получить текущую дату
        now = datetime.now()
        current_date = now.date()

        # Фильтровать данные для текущей даты
        today_data = df[df['time'].dt.date == current_date]

        if not today_data.empty:
            time = today_data['time'].dt.tz_localize(None).tolist()
            shortwave_radiation_instant = today_data['shortwave_radiation_instant'].tolist()
            temperature_2m = today_data['temperature_2m'].tolist()
            windspeed_10m = today_data['windspeed_10m'].tolist()
            relativehumidity_2m = today_data['relativehumidity_2m'].tolist()

            for i in range(len(today_data)):
                book0 = OpenMeteo.objects.create(
                    time=time[i],
                    shortwave_radiation_instant=shortwave_radiation_instant[i],
                    temperature_2m=temperature_2m[i],
                    windspeed_10m=windspeed_10m[i],
                    relativehumidity_2m=relativehumidity_2m[i],
                )

                book0.save()
        else:
            print("No data available for today.")
    else:
        print("Failed to fetch data from the API.")


def BaseUpdate(request):
    lat = 0
    lon = 0

    
    Data.objects.all().delete()

    data = []
    huawei = Huawei.objects.all()
    geolocator = Nominatim(user_agent="192.168.0.111:8000")
    for user in huawei:
        try:
            client = FusionSolarClient(user.u_name, user.p_word, huawei_subdomain=user.sub_domain)
            stats = client.get_station_list()
            for stat in stats:
                lat = stat['latitude']  # Исправление: Замените 'longitude' на 'latitude'
                lon = stat['longitude']
                abs_val = stat['currentPower']  # Исправление: Избегайте использования зарезервированных слов в качестве идентификаторов
                use = stat['dailyEnergy']
                pv = stat['yearEnergy']
                name = stat['nameSearch']
                inverterPower = stat['inverterPower']
                gridConnectedTime = stat['gridConnectedTime']
                location = geolocator.reverse(str(lat)+","+str(lon))
                address = location.raw['address']
                if 'city' in address.keys():
                    hudud=address.get('city')
                if 'region' in address.keys():
                    hudud=address.get('region')
                if 'state' in address.keys():
                    hudud=address.get('state')

                book1 = Data.objects.create(
                    lat= lat,
                    lon= lon,
                    inverterPower=inverterPower,
                    gridConnectedTime= gridConnectedTime,
                    abs_val = abs_val,
                    use = use,
                    pv = pv,
                    name = name,
                    regions = hudud,
                    adress = location,
                )

                book1.save()
                all_books = Data.objects.all()
                print(all_books)
        except:
            pass
    solax_instances = Solax.objects.all()
    for stat in solax_instances:
        try:
            url = "https://solaxcloud.com/proxyApp/proxy/api/getRealtimeInfo.do?tokenId=" + stat.token + "&sn=" + stat.sn

            lat = stat.lat # Change 'longitude' to 'latitude'
            lon = stat.lon
            name = stat.name
            inverterPower = stat.inverterPower

            response = requests.get(url)
            data_array = response.json()

            gridConnectedTime = data_array['result'][1]['uploadTime']
            abs_val = float(data_array['result'][1]['acpower']) / 1000
            use = data_array['result'][1]['yieldtoday']
            pv = data_array['result'][1]['yieldtotal']

            location = geolocator.reverse(str(lat) + "," + str(lon))
            address = location.raw['address']

            if 'city' in address.keys():
                hudud = address.get('city')
            elif 'region' in address.keys():
                hudud = address.get('region')
            elif 'state' in address.keys():
                hudud = address.get('state')
            else:
                hudud = None  # Handle the case when none of the keys match

            book2 = Data.objects.create(
                lat=lat,
                lon=lon,
                inverterPower=inverterPower,
                gridConnectedTime=gridConnectedTime,
                abs_val=abs_val,
                use=use,
                pv=pv,
                name=name,
                regions=hudud,
                adress=location,
            )

            book2.save()
        except:
            pass


    all_books = Data.objects.all()
    # print(all_books)
    regions = ['Andijon Viloyati', 'Buxoro Viloyati', 'Samarqand Viloyati', 'Sirdaryo Viloyati', 'Toshkent',
               'Toshkent Viloyati', "Farg'ona Viloyati", 'Jizzax Viloyati', 'Qashqadaryo Viloyati',
               'Namangan Viloyati', 'Navoiy Viloyati', 'Surxondaryo Viloyati', 'Xorazm Viloyati',
               'Qaraqalpaqstan Respublikasi']
    return render(request, 'index.html', {'regions': regions, 'data': all_books})


# def baza(request):
#     # if request.method == 'POST':
#     #     lon=request.POST['koor0']
#     #     lat=request.POST['koor1']
#     meteo=Meteos.objects.all()
#     #print('salom',len(meteo))    
#     alisher='alisher'


#     # meteo=Meteos.objects.all()
#     # for i in range(len(meteo)):
#     #     folium.Marker([meteo[i].lat, meteo[i].lon], popup=meteo[i].meteoName, tooltip='Tanlang').add_to(marker_cluster)

#     return render(request, 'index.html', {'meteos': meteo, 'alisher':alisher})
# def bazayuklash(request):
#     meteo=Meteos.objects.all()
#     data0 = pd.read_excel('Meteostansiyalar.xlsx', header=None)
#     data=[]
#     for i in range(1,len(data0)):
#         dat=data0.iloc[i]
#         meteo = Meteos(
#             WMO_id = dat[0],
#             placeName = dat[1],
#             meteoName = dat[2],
#             lat = dat[3],
#             lon = dat[4],
#             height = dat[5],
#             period = dat[6])
#        # meteo.save()

#     return redirect('index')

# Create a new book
# First, delete existing records in Solax and Huawei models
# Solax.objects.all().delete()
# Huawei.objects.all().delete()
# # Data for Huawei model
# huawei_data = [
#     ['Ergashali', 'rey19861512', 'region02eu5'],
#     ['husen.xudoyorov', 'amirtex2023', 'region02eu5'],
#     ['zafar1', 'MilliyETK123', 'region02eu5'],
# ]

# # Data for Solax model
# solax_data = [  # 'token, Sn, lat, lon, name, inverterPower
#     ['202307080025017316490211', 'SR72KK7KTH', 41.329857773298535, 69.29082635405092, 'MIB Yunusobod', '50 kW'],
# ]

# for user_data in huawei_data:
#     huawei_obj = Huawei.objects.create(
#         u_name=user_data[0],
#         p_word=user_data[1],
#         sub_domain=user_data[2],
#     )
#     huawei_obj.save()

# # Create Solax objects
# for user_data in solax_data:
#     solax_obj = Solax.objects.create(
#         token=user_data[0],
#         sn=user_data[1],
#         lat=user_data[2],
#         lon=user_data[3],
#         name=user_data[4],
#         inverterPower=user_data[5],
#     )

#     # Save the Solax object
#     solax_obj.save()

# addd = Admin.objects.create(
#     a_name = "Index4838",
#     a_word = "Komiljonovich99"
# )

# addd.save()






    

@csrf_exempt
def my_view(request):
    global closestMeteoName_fin, meteoId, lat, lon
    lon = 0
    solarID = [3, 6, 8, 16, 20, 24, 27, 29, 43, 49, 51, 67, 76, 80, 82, 87, 98, 100, 102, 103, 104, 106]
    meteoId = 0  # Initialize meteoId with a default value
    closestMeteoName_fin = 0  # Initialize with a default value
    regions = ['Andijon Viloyati','Buxoro Viloyati','Samarqand Viloyati','Sirdaryo Viloyati','Toshkent', 'Toshkent Viloyati', "Farg'ona Viloyati", 'Jizzax Viloyati','Qashqadaryo Viloyati',
                'Namangan Viloyati','Navoiy Viloyati','Surxondaryo Viloyati','Xorazm Viloyati','Qaraqalpaqstan Respublikasi']
    data= Data.objects.all()
    meteoData = MeteoData.objects.all()

    queryset_real = Real.objects.all()
    data_r = list(queryset_real.values())
    r_data = pd.DataFrame(data_r)
    queryset_GetData = GetData.objects.all()
    data_g = list(queryset_GetData.values())
    g_data = pd.DataFrame(data_g)
    
    if request.method == 'POST':
        closestMeteoName_fin=request.POST['closestMeteoName_fin']
        lat = request.POST['closestMeteoLat']
        lon = request.POST['closestMeteoLon']
        closestMeteoName_fin1 = request.POST['closestMeteoName_fin1']
        closestMeteoName1 = request.POST['closestMeteoName1']
        closestMeteoLat1 = request.POST['closestMeteoLat1']
        closestMeteoLon1 = request.POST['closestMeteoLon1']


        
        met = list(meteoData.values())
        meteoData_one = pd.DataFrame(met)
        meteoData_one['meteo_id'] = meteoData_one['meteo_id'].astype(float)
        meteoData_one1 = meteoData_one[~meteoData_one['meteo_id'].isin(solarID)]
        solarID22 = meteoData_one[meteoData_one['meteo_id'].isin(solarID)]
        meteoData_one2 = meteoData_one1[meteoData_one1['meteo_id'] == str(closestMeteoName_fin)]
        if not meteoData_one2.empty:
            closest_station_id, closest_distance = find_closest_solar_id(solarID22, meteoData_one2)
            # Further processing using closest_station_id and closest_distance
        else:
            closest_station_id = closestMeteoName_fin
            closest_distance = None
            print("No matching data found in meteoData_one1 for the given closestMeteoName_fin")

        

        # Заданные координаты
        OpenMeteos(lat, lon)
        # print(f"ID ближайшей метеостанции: {closest_station_id}")
        # print(f"Расстояние до нее: {closest_distance} км")
        # print(closestMeteoName_fin)

        # print(lat, lon)
        for data in meteoData:
            if closestMeteoName_fin == data.meteo_id:
                meteoId = closestMeteoName_fin  # Assign the value if there's a match
                
        # print(closestMeteoName_fin)


        queryset = OpenMeteo.objects.all()
        data = list(queryset.values())
        f_data = pd.DataFrame(data)
        selected_rows = MeteoData.objects.filter(meteo_id__in=solarID)
        unique_rows = {}
        for row in selected_rows:
            unique_rows[row.meteo_id] = row
        unique_rows_list = list(unique_rows.values())
        data_solar = pd.DataFrame(unique_rows_list)
        
        
        
        u_data = r_data[r_data['meteo_id'] == str(closest_station_id)]
        r_data3 = r_data[r_data['meteo_id'] == str(closestMeteoName_fin)]
        r_data1 = pd.merge(r_data3, u_data, on=['time'], how='inner')
        current_date = datetime.now().date()
        specific_date = current_date.strftime('%Y-%m-%d')
        r_data1['time'] = pd.to_datetime(r_data1['time'])
        rdata_4time = r_data1['time'].dt.strftime('%Y-%m-%d')
        r_data1_filtered = r_data1[rdata_4time == specific_date]
        x1 = r_data1_filtered['time']
        z1 = r_data1_filtered['temp_y']
        a1 = r_data1_filtered['rel_hum_y']
        b1 = r_data1_filtered['windspeed_y']
        y1 = r_data1_filtered['solarradiation_y']
        
        # r_data = r_data.dropna()
        # r_data_2 = r_data_2.dropna()
        x = f_data['time']
        y = f_data['shortwave_radiation_instant']
        z = f_data['temperature_2m']
        a = f_data['relativehumidity_2m']
        b = f_data['windspeed_10m']
        
        g_data = g_data[g_data['get_id'] == str(closestMeteoName_fin1)]
        g_data['time'] = pd.to_datetime(r_data1['time'])
        gdata_4time = g_data['time'].dt.strftime('%Y-%m-%d')
        g_data_filtered = g_data[gdata_4time == specific_date]
        
        
        new_df=pd.DataFrame()
        new_df['time'] = g_data_filtered['time']
        new_df['get_id']=dict
        new_df['abs_power'] = g_data_filtered['abs_power'].diff()
        new_df['abs_power'] = new_df['abs_power'].shift(-1)
        new_df=new_df.dropna()
        new_df['abs_power'] = new_df['abs_power']*1000
        new_df['time'] = new_df['time'].dt.round('30min')
        x_g = new_df['time']
        y_g = new_df['abs_power']
        print(closestMeteoName_fin1)

        fig, ax = plt.subplots(figsize=(6, 2.5))
        ax.plot(x, y, marker='o', linestyle='-', label='Prediction Data')
        ax.plot(x1, y1, marker='.', linestyle='-', label='Real Data')
        ax.set_xlabel('Time')
        ax.set_ylabel('Shortwave Radiation W/m2')
        ax.set_title(f'Shortwave Radiation ')
        ax.legend()

        
        # Create a sample Matplotlib plot
        fig1, ax1 = plt.subplots(figsize=(6, 2.5))
        ax1.plot(x, z, marker='o', linestyle='-', label='Prediction Data')
        ax1.plot(x1, z1, marker='.', linestyle='-', label='Real Data')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Temperature, C')
        ax1.set_title(f'Temperature ')
        ax1.legend()

        # print(f_data)


        # Create a sample Matplotlib plot
        fig2, ax2 = plt.subplots(figsize=(6, 2.5))
        ax2.plot(x, a, marker='o', linestyle='-', label='Prediction Data')
        ax2.plot(x1, a1, marker='o', linestyle='-', label='Real Data')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Relative Humidity, %')
        ax2.set_title(f'Relative Humidity ')
        ax2.legend()


        # Create a sample Matplotlib plot
        fig3, ax3 = plt.subplots(figsize=(6, 2.5))
        ax3.plot(x, b, marker='o', linestyle='-', label='Prediction Data')
        ax3.plot(x1, b1, marker='o', linestyle='-', label='Real Data')
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Wind Speed, m/s')
        ax3.set_title(f'Wind Speed ')
        ax3.legend()


        fig4, ax4 = plt.subplots(figsize=(6, 2.5))
        ax4.bar(x_g, y_g / 1000, label='Real Quvvat', width=0.015, color='skyblue')  # Устанавливаем ширину и цвет столбцов
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Power, kW/h')
        ax4.set_title(f'Fotoelektrik stansiya {closestMeteoName1}')
        ax4.legend()

        fig.savefig('foo1.png')
        fig1.savefig('foo2.png')
        fig2.savefig('foo3.png')
        fig3.savefig('foo4.png')
        fig4.savefig('foo5.png')

        
        mpld3.save_html(fig, 'templates/plot1_html.html')
        mpld3.save_html(fig1, 'templates/plot2_html.html')
        mpld3.save_html(fig2, 'templates/plot3_html.html')
        mpld3.save_html(fig3, 'templates/plot4_html.html')
        mpld3.save_html(fig4, 'templates/plot5_html.html')
        plt.close(fig)
        plt.close(fig1)
        plt.close(fig2)
        plt.close(fig3)
        plt.close(fig4)
    return render(request, 'index.html', {
        'regions': regions, 
        'data': data
    })

def serialize_meteoData(meteoData):
    # Сериализуем QuerySet в формат JSON
    result = serialize('json', meteoData)

    return result

def serialize_data(data):
    # Сериализуем QuerySet в формат JSON
    serialized_data = serialize('json', data)

    # Преобразуем строку JSON в объект Python
    deserialized_data = json.loads(serialized_data)

    # Создаем список для сохранения результата
    result = []

    # Проходимся по объектам в deserialized_data и извлекаем нужные поля
    for item in deserialized_data:
        fields = item['fields']
        serialized_item = {
            'lat': fields['lat'],
            'lon': fields['lon'],
            'inverterPower': fields['inverterPower'],
            'gridConnectedTime': fields['gridConnectedTime'],
            'abs_val': fields['abs_val'],
            'use': fields['use'],
            'pv': fields['pv'],
            'name': fields['name'],
            'regions': fields['regions'],
            'adress': fields['adress'],
            'get_id': fields['get_id'],
        }
        result.append(serialized_item)

    return result

def serialize_GetData(data):
    # Сериализуем QuerySet в формат JSON
    serialized_data = serialize('json', data)

    # Преобразуем строку JSON в объект Python
    deserialized_data = json.loads(serialized_data)

    # Создаем список для сохранения результата
    result = []

    # Проходимся по объектам в deserialized_data и извлекаем нужные поля
    for item in deserialized_data:
        fields = item['fields']
        serialized_item = {
            'time': fields['time'],
            'get_id': fields['get_id'],
            'real_power': fields['real_power'],
            'abs_power': fields['abs_power'],
            'year_power': fields['year_power'],
        }
        result.append(serialized_item)

    return result

def get_data(request):
    data = Data.objects.all()  # Здесь вы можете использовать нужный вам QuerySet для получения данных
    serialized_data = serialize_data(data)  # Предполагается, что у вас есть функция для сериализации данных в JSON
    return JsonResponse(serialized_data, safe=False)

# def FesData(request):
#     getData = GetData.objects.all()  # Здесь вы можете использовать нужный вам QuerySet для получения данных
#     GetDatas = serialize_data(getData)  # Предполагается, что у вас есть функция для сериализации данных в JSON
#     return JsonResponse(GetDatas, safe=False)


def get_meteoData(request):
    meteoData = MeteoData.objects.all()
    meteoData_list = [{'meteo_id': item.meteo_id, 'lat': item.lat, 'lon': item.lon, 'name': item.name} for item in meteoData]
    return JsonResponse(meteoData_list, safe=False)


# MeteoData.objects.all().delete()
# data_txt = pd.read_csv('data.txt', header=None, sep=';')
# data_txt.columns = ['id', 'lat', 'lon', 'name']
# print(data_txt)
# for data in range(len(data_txt)):
#     book1 = MeteoData.objects.create(
#         meteo_id=data_txt['id'][data],
#         lat=data_txt['lat'][data],
#         lon=data_txt['lon'][data],
#         name=data_txt['name'][data],
#     )
# book1.save()
# all_books = MeteoData.objects.all()
# for i in all_books:
#     print(i.meteo_id)




def download_real():
    import datetime
    # Disable insecure request warnings (not recommended for production use)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # List of station IDs that measure radiation
    radiation_station_ids = [3, 6, 8, 16, 20, 24, 27, 29, 43, 49, 51, 67, 76, 80, 82, 87, 98, 100, 102, 103, 104, 106]


    try:
        huawei = Huawei.objects.all()
        for i in huawei:
            try:
                client = FusionSolarClient(i.u_name, i.p_word, huawei_subdomain=i.sub_domain)
                stats = client.get_station_list()
                for stat in stats:
                    now = datetime.datetime.now()
                    onlydatetime = now.strftime("%Y-%m-%d %H:%M:%S")
                    currentPower = stat['currentPower']
                    dailyEnergy = stat['dailyEnergy']
                    yearEnergy = stat['yearEnergy']
                    dnId = stat['dnId']
                    client.log_out()
                
                    book1 = GetData.objects.create(
                        time=onlydatetime,
                        get_id=dnId,
                        real_power=currentPower,  # Access other columns similarly
                        abs_power=dailyEnergy,
                        year_power=yearEnergy,
                    )

                    book1.save()
                    print("Write GetData Compleate ", onlydatetime)

            except:
                pass

        for station_id in range(107):
            try:
                url = 'https://data.meteo.uz/map/awd/getStation'
                data = {'token': 'Dte9F3Iq0xvYD0KsRmCPV1CzZqtqmbdmCwOwNmIK', 'id': station_id}
            
                response = requests.post(url, data=data, verify=False) #verify=False)
            
                try:
                    if response.status_code == 200:
                        response_data = response.json()
                        switch_case0 = response_data['Stations']['Sources']['Variables']
                        variable_names = [variable['VariableName'] for variable in switch_case0]
                        station_name = response_data['Stations']['StationName']
                    
                        values = [variable['Value']['Value'] for variable in switch_case0]
                        meastime = response_data['Stations']['Sources']['Variables'][2]['Value']['Meastime']
                        datetime_obj = datetime.datetime.fromisoformat(meastime[:-1]) + datetime.timedelta(hours=5)
                    
                        date = datetime_obj.date()
                        time_val = datetime_obj.time()
                    
                        dff = pd.DataFrame({'Meastime': [meastime]})
                        dff.insert(0, 'StationName', station_name)
                    
                        for variable_name, value in zip(variable_names, values):
                            dff[variable_name] = value

                        if station_id in radiation_station_ids:
                            solar_value = switch_case0[21]['Value']['Value']
                        
                            if station_id<=53:
                                book0 = Real.objects.create(
                                    time=datetime.datetime.strptime(f"{date} {time_val}", '%Y-%m-%d %H:%M:%S'),
                                    meteo_id=station_id,
                                    temp=dff['Temp.Dry.10min.Average'][0],  # Access other columns similarly
                                    t_air_min=dff['Temp.Dry.10min.Min'][0],
                                    t_air_max=dff['Temp.Dry.10min.Max'][0],
                                    rel_hum=dff['RelHumidity.10min.Average'][0],
                                    windspeed=dff['Wind.Speed.10min.Average'][0],
                                    winddir=dff['Wind.Dir.10min.Average'][0],
                                    solarradiation=solar_value,
                                )
                                book0.save()
                                print("Write Compleate")
                            else:
                                book0 = Real.objects.create(
                                    time=datetime.datetime.strptime(f"{date} {time_val}", '%Y-%m-%d %H:%M:%S'),
                                    meteo_id=station_id,
                                    temp=dff['Temp.Dry.10min.Average'][0],  # Access other columns similarly
                                    t_air_min=dff['Temp.Dry.10min.Min'][0],
                                    t_air_max=dff['Temp.Dry.10min.Max'][0],
                                    rel_hum=dff['RelHumidity.10min.Average'][0],
                                    windspeed=dff['Wind.Speed.10min.Average'][0],
                                    winddir=dff['Wind.Dir.10min.Average'][0],
                                    solarradiation=solar_value / 2
                                )
                                book0.save()
                                print("Write Compleate")

                        else:
                            book0 = Real.objects.create(
                                time=datetime.datetime.strptime(f"{date} {time_val}", '%Y-%m-%d %H:%M:%S'),
                                meteo_id=station_id,
                                temp=dff['Temp.Dry.10min.Average'][0],  # Access other columns similarly
                                t_air_min=dff['Temp.Dry.10min.Min'][0],
                                t_air_max=dff['Temp.Dry.10min.Max'][0],
                                rel_hum=dff['RelHumidity.10min.Average'][0],
                                windspeed=dff['Wind.Speed.10min.Average'][0],
                                winddir=dff['Wind.Dir.10min.Average'][0],
                                solarradiation='nan',
                            )

                            print("Write Compleate NOT SOLAR")
                            book0.save()

                    else:
                        print('Error:', response.status_code)
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")
            except Exception as e:
                print('No internet connection', e)
        time.sleep(600)
    except Exception as e:
        print("ERROR ", e)



    

  


   

all_books = GetData.objects.all()
for i in all_books:
    print(i.time)
        
# GetData.objects.all().delete()
# Real.objects.all().delete()
        
# df = pd.read_csv('2023-10-19.txt', header=None, sep='\t')        
# df.columns = ['time', 'get_id', 'real_power', 'abs_power', 'year_power'] 
# for i in range(len(df)):
#     book0 = GetData.objects.create(
#         time=df['time'][i],
#         get_id=df['get_id'][i],
#         real_power=df['real_power'][i],
#         abs_power=df['abs_power'][i],
#         year_power=df['year_power'][i],
#     )

#     print("Write GetData Compleate")
#     book0.save()
        
        
# Real.objects.all().delete()
# filepath1 = 'D:/new_desktop/SolarMap/map/real/'
# now = datetime.now()
# filename1 = filepath1 + now.strftime("%Y-%m-%d") + '_solar.txt'
# data_r1 = pd.read_csv(filename1,  sep='\t')
# data_r1.columns = ['time', 'meteo_id', 'temp', 't_air_min', 't_air_max','rel_hum', 'windspeed', 'winddir','solarradiation']
# print(data_r1.columns)
# for index, row in data_r1.iterrows():
#     # Access the 'datetime_column' value for the current row
#     datetime_str = row['time']  # Replace 'datetime_column' with the actual column name

#     # Parse the ISO format datetime string
#     parsed_datetime = parse_datetime(datetime_str)

#     book0 = Real.objects.create(
#         time=parsed_datetime,
#         meteo_id=row['meteo_id'],
#         temp=row['temp'],  # Access other columns similarly
#         t_air_min=row['t_air_min'],
#         t_air_max=row['t_air_max'],
#         rel_hum=row['rel_hum'],
#         windspeed=row['windspeed'],
#         winddir=row['winddir'],
#         solarradiation=row['solarradiation'],
#     )

#     book0.save()

# queryset_real = Real.objects.all()
# data_r = list(queryset_real.values())
# r_data = pd.DataFrame(data_r)
# print(r_data)

# Data.objects.all().delete()

# data = []
# huawei = Huawei.objects.all()
# geolocator = Nominatim(user_agent="192.168.0.111:8000")
# for user in huawei:
#     try:
#         client = FusionSolarClient(user.u_name, user.p_word, huawei_subdomain=user.sub_domain)
#         stats = client.get_station_list()
#         for stat in stats:
#             lat = stat['latitude']  # Исправление: Замените 'longitude' на 'latitude'
#             lon = stat['longitude']
#             abs_val = stat['currentPower']  # Исправление: Избегайте использования зарезервированных слов в качестве идентификаторов
#             use = stat['dailyEnergy']
#             pv = stat['yearEnergy']
#             name = stat['nameSearch']
#             inverterPower = stat['inverterPower']
#             gridConnectedTime = stat['gridConnectedTime']
#             location = geolocator.reverse(str(lat)+","+str(lon))
#             address = location.raw['address']
#             dnId = stat['dnId']
#             if 'city' in address.keys():
#                 hudud=address.get('city')
#             if 'region' in address.keys():
#                 hudud=address.get('region')
#             if 'state' in address.keys():
#                 hudud=address.get('state')

#             book1 = Data.objects.create(
#                 lat= lat,
#                 lon= lon,
#                 inverterPower=inverterPower,
#                 gridConnectedTime= gridConnectedTime,
#                 abs_val = abs_val,
#                 use = use,
#                 pv = pv,
#                 name = name,
#                 regions = hudud,
#                 adress = location,
#                 get_id=dnId,
#             )

#             book1.save()
#             all_books = Data.objects.all()
#             print(all_books)
#     except:
#         pass
        
