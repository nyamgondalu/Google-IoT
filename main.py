import sys
import Adafruit_DHT
import datetime
import time
import jwt
import paho.mqtt.client as mqtt











# Define some project-based variables to be used below. This should be the only
# block of variables that you need to edit in order to run this script

ssl_private_key_filepath = '/home/pi/Desktop/Google-IoT/certs/rsa_private.pem'
ssl_algorithm = 'RS256' # Either RS256 or ES256
root_cert_filepath = '/home/pi/Desktop/Google-IoT/certs/roots.pem'
project_id = 'linen-striker-227009'
gcp_location = 'asia-east1'
registry_id = 'Pi3-DHT11-Nodes'
device_id = 'Pi3-DHT11-Node'

# end of user-variables

cur_time = datetime.datetime.utcnow()

def create_jwt():
  token = {
      'iat': cur_time,
      'exp': cur_time + datetime.timedelta(minutes=60),
      'aud': project_id
  }

  with open(ssl_private_key_filepath, 'r') as f:
    private_key = f.read()

  return jwt.encode(token, private_key, ssl_algorithm)

_CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, gcp_location, registry_id, device_id)
_MQTT_TOPIC = '/devices/{}/events'.format(device_id)

client = mqtt.Client(client_id=_CLIENT_ID)
# authorization is handled purely with JWT, no user/pass, so username can be whatever
client.username_pw_set(
    username='unused',
    password=create_jwt())

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))

def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')

client.on_connect = on_connect
client.on_publish = on_publish

client.tls_set(ca_certs=root_cert_filepath) # Replace this with 3rd party cert if that was used when creating registry
client.connect('mqtt.googleapis.com', 8883)
client.loop_start()

# Could set this granularity to whatever we want based on device, monitoring needs, etc
temperature = 0
humidity = 0
cur_humidity=0
cur_temp=0



while True:
	cur_humidity, cur_temp = Adafruit_DHT.read_retry(11, 4)
	#print("Temp: %d C" % temperature)
	#print("Humidity: %d %%" % humidity)



  	if cur_temp == temperature and cur_humidity == humidity:
      		time.sleep(1)
      		continue

  	temperature = cur_temp
  	humidity = cur_humidity
  	#payload = '{{ "ts": {}, "temperature": {}, "humidity": {} }}'.format(int(time.time()), temperature, `																																																																																																																																																																		humidity)
  	payload = '{{ "ts": {}, "temperature": {}, "humidity": {} }}'.format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))), temperature, humidity)
  	client.publish(_MQTT_TOPIC, payload, qos=1)

  	print("{}\n".format(payload))

  	time.sleep(1)

client.loop_stop()
