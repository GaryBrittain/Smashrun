import urllib, urllib2, json
from stravalib.client import Client
from stravalib import unithelper
import dateutil.parser as parser
from pytz import timezone

activityId = 321998419

client = Client(access_token="#YOUR ACCESS TOKEN#")
activity = client.get_activity(activityId)

localtz = timezone(str(activity.timezone))

types = ['distance', 'latlng', 'time', 'altitude', 'moving']

streams = client.get_activity_streams(activityId, types=types, resolution='high')

latList = []
lngList = []
for lat,lng in streams['latlng'].data:
  latList.append(lat)
  lngList.append(lng)

waypointCount = len(streams['time'].data)
duration = []
cumulPause = 0

for idx in range(0,waypointCount):
  if idx == 0:
    duration.append(streams['time'].data[idx])
    current = streams['time'].data[idx]
  elif streams['moving'].data[idx] == True:
    duration.append(int(streams['time'].data[idx]) - cumulPause)
    current = (streams['time'].data[idx])
  elif streams['moving'].data[idx] == False and streams['moving'].data[idx-1] == False:
    duration.append(duration[idx-1])
    cumulPause = cumulPause + (streams['time'].data[idx] - streams['time'].data[idx-1])
  elif streams['moving'].data[idx] == False:
    duration.append(int(current - cumulPause))
    cumulPause = cumulPause + (streams['time'].data[idx] - streams['time'].data[idx-1])

distance = []
for idx in range(0,waypointCount):
  distance.append(float(streams['distance'].data[idx] / 1000))

parameters = {
  'activityType': "running",
  'distance': float(unithelper.kilometers(activity.distance)),
  'duration': activity.moving_time.seconds,
  'startDateTimeLocal': localtz.localize(activity.start_date_local).isoformat(),
  'note': activity.name,
  'externalId': activity.id,
  'recordingKeys':["latitude","longitude","duration","clock","distance","elevation"],
  'recordingValues': (latList,lngList,duration,streams['time'].data,distance,streams['altitude'].data)
}

headers = {
    'Content-Type': "application/json",
    'Authorization': "Bearer #YOUR ACCESS TOKEN#"
}

data = json.dumps(parameters)
url = "https://api.smashrun.com/v1/my/activities"
req = urllib2.Request(url,data,headers)
response = urllib2.urlopen(req)
print response.read()
