import pycurl, json
from StringIO import StringIO
import RPi.GPIO as GPIO
from sense_hat import SenseHat
import time
from time import asctime

sense = SenseHat()
sense.clear()

cold = 30
hot = 40
pushMessage = ""

OFFSET_LEFT = 1
OFFSET_TOP = 2

NUMS = [
  1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,  #0
  0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,  #1
  1,1,1,0,0,1,0,1,0,1,0,0,1,1,1,  #2
  1,1,1,0,0,1,1,1,1,0,0,1,1,1,1,  #3
  1,0,0,1,0,1,1,1,1,0,0,1,0,0,1,  #4
  1,1,1,1,0,0,1,1,1,0,0,1,1,1,1,  #5
  1,1,1,1,0,0,1,1,1,1,0,1,1,1,1,  #6
  1,1,1,0,0,1,0,1,0,1,0,0,1,0,0,  #7
  1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,  #8
  1,1,1,1,0,1,1,1,1,0,0,1,0,0,1   #9
  ]

# Displays single digit (0-9)
def show_digit(val, xd, yd, r, g, b):
  offset = val * 15
  for p in range(offset, offset + 15):
    xt = p % 3
    yt = (p - offset)//3
    sense.set_pixel(xt + xd, yt + yd, r*NUMS[p], g*NUMS[p], b*NUMS[p])

# Displays two digit (0-99)
def show_number(val, r, g, b):
  abs_val = abs(val)
  tens = abs_val//10
  units = abs_val % 10
  if (abs_val > 9):
    show_digit(tens, OFFSET_LEFT, OFFSET_TOP, r, g, b)
  show_digit(units, OFFSET_LEFT + 4, OFFSET_TOP, r, g, b)

temperature = round(sense.get_temperature())
pressure = round(sense.get_pressure())
humidity = round(sense.get_humidity())

message = "Temperature = {0} Pressure = {1} Humidity = {2} .".format(temperature, pressure, humidity)

#setup instapush variable by adding instapush application ID
appID = ""

#add your instapush application secret
appSecret = ""
pushEvent = "event name here"

#use curl to push to instapush api
c = pycurl.Curl()

#set api url
c.setopt(c.URL, 'https://api.instapush.im/v1/post')

#setup custom headers for authentication variables and custom type
c.setopt(c.HTTPHEADER, ['x-instapush-appid: ' + appID,
'x-instapush-appsecret: ' + appSecret,
'Content-Type: application/json'])

#use this to pass the response from our push api call
buffer = StringIO()

def p(pushMessage):
  json_fields = {}

  json_fields['event'] = pushEvent
  json_fields['trackers'] = {}
  json_fields['trackers']['message'] = pushMessage
  print(json_fields)
  postfields = json.dumps(json_fields)

  c.setopt(c.POSTFIELDS, postfields)

  c.setopt(c.WRITEFUNCTION, buffer.write)

  c.setopt(c.VERBOSE, True)

while True:

  temperature = round(sense.get_temperature())
  pressure = round(sense.get_pressure())
  humidity = round(sense.get_humidity())

  message = "Temperature = {0} Pressure = {1} Humidity = {2} .".format(temperature, pressure, humidity)

  time.sleep(4)
  log = open('weather.txt', "a")
  now = str(asctime())
  temperature = int(temperature)
  show_number(temperature, 200, 0, 60)
  temp1 = temperature

  log.write(now + '' + message + '\n')
  print(message)
  log.close()
  time.sleep(5)

  if temperature >= hot:
    pushMessage = 'Its hot: ' + message
    p(pushMessage)
    c.perform()
    body = buffer.getvalue()
    pushMessage = ""
  elif temperature < cold:
    pushMessage = 'Its cold: ' + message
    p(pushMessage)
    c.perform()
    body = buffer.getvalue()
    pushMessage = ""

  #print the message
  print(body)

  #reset the buffer
  buffer.truncate(0)
  buffer.seek(0)

#cleanup
c.close()
GPIO.cleanup()