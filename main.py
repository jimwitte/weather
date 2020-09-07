# weather for kickapoo state park
import requests
from datetime import datetime, timedelta
import pprint
import os
from dotenv import load_dotenv

load_dotenv()
pp = pprint.PrettyPrinter(indent=4)

OUTPUT_FILE = os.getenv("OUTPUT_FILE")
TOKEN = os.getenv("TOKEN")
TIME_FORMAT = "%m/%d/%Y %H:%M"

END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(hours=48)

def total_recent_rainfall(response_data):
    """ calculate total rainfall """
    total_rainfall = 0
    summary = ''
    if response_data.get('location', None) is None:
            return ""
    for value in reversed(response_data['location']['values']):
        total_rainfall = total_rainfall + value['precip']
        this_date = datetime.strptime(value['datetimeStr'], "%Y-%m-%dT%H:%M:%S%z").strftime(TIME_FORMAT)
        summary = summary + f"""<tr><th scope="row">{str(this_date)}</th><td>{str(value['precip'])}in</td></tr>"""
    return f"""
        <tr><th scope="row">48h rainfall</th><td>{str(total_rainfall)}in</td></tr>
        {summary}
    """

def current_conditions(response_data):
    """ current conditions printout """
    if response_data.get('location', None) is None:
        return ""
    l = response_data['location']['currentConditions']
    return f"""
    <tr><th scope=“row”>Temperature</th><td>{l['temp']}F</td></tr>
    <tr><th scope=“row”>Humidity</th><td>{l['humidity']}%</td></tr>
    <tr><th scope=“row”>Dew point</th><td>{l['dew']}F</td></tr>
    <tr><th scope=“row”>Precipitation</th><td>{l['precip']} in</td></tr>
    <tr><th scope=“row”>Winds</th><td>{l['wspd']} mph, gust {l['wgust']} mph</td></tr>
    <tr><th scope=“row”>Wind Direction</th><td>{l.get('wdir', None)} deg</td></tr>
    <tr><th scope=“row”>Snowdepth</th><td>{l['snowdepth']}</td></tr>
    <tr><th scope=“row”>Sunrise</th><td>{datetime.strptime(l['sunrise'], "%Y-%m-%dT%H:%M:%S%z").strftime(TIME_FORMAT)}</td></tr>
    <tr><th scope=“row”>Sunset</th><td>{datetime.strptime(l['sunset'], "%Y-%m-%dT%H:%M:%S%z").strftime(TIME_FORMAT)}</td></tr>
    """

weather_history_post_fields = {
    "aggregateHours": 24,
    "combinationMethod": "aggregate",
    "startDateTime": START_DATE.isoformat('T', 'seconds'),
    "endDateTime": END_DATE.isoformat('T', 'seconds'),
    "collectStationContributions": True,
    "includeAstronomy": True,
    "maxStations": -1,
    "maxDistance": -1,
    "includeNormals": False,
    "sendAsDatasource": True,
    "contentType": "json",
    "unitGroup": "us",
    "locationMode": "single",
    "key": TOKEN,
    "sourceDatasourceTable": "{\"name\":\"WxSourceData1\",\"id\":\"WxSourceData1\",\"isPrimary\":true,\"analyzeLevels\":false,\"rowDateTimeColumnIndex\":-1,\"defaultDateTimeFormat\":\"yyyy-M-d'T'H:m:s\",\"columns\":[{\"isKey\":true,\"name\":\"ID\",\"id\":\"id\",\"type\":\"string\"},{\"isKey\":false,\"name\":\"Name\",\"id\":\"name\",\"type\":\"string\"},{\"isKey\":false,\"name\":\"Address\",\"id\":\"address\",\"type\":\"string\"}],\"rows\":[[\"db8d4686e7\",\"kmb trailhead\",\"40.152578, -87.715877\"]],\"layerDataContext\":{\"FieldJoins\":\"{}\",\"useGeoJsonGeometry\":\"true\",\"attributeId\":\"id\",\"shapeType\":\"1\",\"onDemandTileGeneration\":\"true\",\"joinLayerColumns\":\"address\",\"contextType\":\"6\",\"attributeName\":\"\",\"FieldValues\":\"{}\",\"addressFields\":\"address\"}}"
}

weather_forecast_post_fields = {
  "aggregateHours": 24,
  "combinationMethod": "aggregate",
  "includeAstronomy": True,
  "sendAsDatasource": True,
  "contentType": "json",
  "unitGroup": "us",
  "locationMode": "single",
  "key": TOKEN,
  "sourceDatasourceTable": "{\"name\":\"WxSourceData1\",\"id\":\"WxSourceData1\",\"isPrimary\":true,\"analyzeLevels\":false,\"rowDateTimeColumnIndex\":-1,\"defaultDateTimeFormat\":\"yyyy-M-d'T'H:m:s\",\"columns\":[{\"isKey\":true,\"name\":\"ID\",\"id\":\"id\",\"type\":\"string\"},{\"isKey\":false,\"name\":\"Name\",\"id\":\"name\",\"type\":\"string\"},{\"isKey\":false,\"name\":\"Address\",\"id\":\"address\",\"type\":\"string\"}],\"rows\":[[\"db8d4686e7\",\"kmb trailhead\",\"40.152578, -87.715877\"]],\"layerDataContext\":{\"FieldJoins\":\"{}\",\"useGeoJsonGeometry\":\"true\",\"attributeId\":\"id\",\"shapeType\":\"1\",\"onDemandTileGeneration\":\"true\",\"joinLayerColumns\":\"address\",\"contextType\":\"6\",\"attributeName\":\"\",\"FieldValues\":\"{}\",\"addressFields\":\"address\"}}"
}


history_request = requests.post(
    'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history',
    data=weather_history_post_fields
)

# forecast_request = requests.post(
#     'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/forecast',
#     data=weather_forecast_post_fields
# )

# pp.pprint(history_request.json())

total_rainfall = total_recent_rainfall(history_request.json())
# current_conditions = current_conditions(forecast_request.json())

page = f"""<!DOCTYPE html>
<html lang="en">
<head><title>Kickapoo State Recreation Area Illinois Recent Rainfall</title>
<style>
body {{
  font-family: verdana;
  font-size: 32px;
}}
table {{
    border-collapse: collapse;
    border: 1pt black solid;
    width: 100%;

}}
td {{
    padding: 6pt;
    border: 1pt black solid;
    text-align: left;
    padding-left: 15pt;
}}
th {{ 
    background-color: lightblue;
    text-align: right;
    border: 1pt black solid;
    padding: 6pt;
}}
h1 {{ 
    margin-bottom: 25pt;
    margin-top: 0;
    font-size: 1.1em;
}}
</style>
</head>
<body>
<h1>Kickapoo State Recreation Area Illinois Recent Rainfall</h1>
<table>
<tr><th colspan="2" style="text-align: center;">Rainfall Totals</th></tr>
{total_rainfall}
{current_conditions}
</table>
<p style="font-size: .6em;">{END_DATE.strftime(TIME_FORMAT)} refreshed every 60 minutes.</p>
</body></html>
"""

webpage = open(OUTPUT_FILE, 'w')
webpage.write(page)