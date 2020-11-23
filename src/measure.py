from multiprocessing import Process, Queue

def flowCheck(queue: Queue):
  import time
  import datetime
  import RPi.GPIO as GPIO  
  try:
    GPIO.setmode(GPIO.BCM)
    # GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.  
    # Both ports are wired to connect to GND on button press.  
    # So we'll be setting up falling edge detection for both  
    GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    totalEvents = 0
    events = 0
    def callback(o):
      nonlocal events, totalEvents
      events = events + 1
      totalEvents = totalEvents + 1

    GPIO.add_event_detect(19, GPIO.RISING, callback=callback)

    while True:
      lastStart = time.time()
      time.sleep(1.0)
      pulses_per_liter = 60 * 6.6
      liters_flown_total = totalEvents / pulses_per_liter
      liters_flown_in_interval = events / pulses_per_liter

      interval = time.time() - lastStart
      liters_per_second = liters_flown_in_interval / interval

      date = datetime.datetime.utcnow()
      now = date.timestamp()

      measurement = {
        "measurement": "flow",
        "time": int(now*1e3),
        "fields": {
          "pulses": events,
          "totalPulses": totalEvents,
          "instantaneous": liters_per_second,
          "total": liters_flown_total,
        }
      }
      queue.put_nowait(measurement)
      
      events = 0


  except KeyboardInterrupt:  
    print("cleanup")
    # GPIO.cleanup()

def measurement(queue: Queue):
  import busio
  import digitalio
  import board
  import adafruit_mcp3xxx.mcp3008 as MCP
  from adafruit_mcp3xxx.analog_in import AnalogIn
  import time
  import datetime

  # from influxdb import InfluxDBClient

  # create the spi bus
  spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

  # create the cs (chip select)
  cs = digitalio.DigitalInOut(board.D13)

  # create the mcp object
  mcp = MCP.MCP3008(spi, cs, ref_voltage=5)

  chan0 = AnalogIn(mcp, MCP.P0)
  chan1 = AnalogIn(mcp, MCP.P1)

  print("Starting...?")

  while True:
    date = datetime.datetime.utcnow()
    now = date.timestamp()

    measurement = {
      "measurement": "adc",
      "time": int(now*1e3),
      "fields": {
        "value0": chan0.value,
        "voltage0": chan0.voltage,
        "value1": chan1.value,
        "voltage1": chan1.voltage
      }
    }
    queue.put_nowait(measurement)
    time.sleep(0.01)

def storage(queue: Queue):
  import time
  from influxdb import InfluxDBClient
  client = InfluxDBClient('localhost', 8086, 'waterrig', 'waterrigpw', 'watertestrig')

  while True:
    batch = []
    while len(batch) < 20:
      batch.append(queue.get())

    print("Writing batch of points")
    client.write_points(batch, time_precision="ms")

if __name__ == '__main__':
  q = Queue()
  measurementProcess = Process(target=measurement, args=(q,))
  storageProcess = Process(target=storage, args=(q,))
  flowCheckProcess = Process(target=flowCheck, args=(q,))

  measurementProcess.start()
  storageProcess.start()
  flowCheckProcess.start()

  measurementProcess.join()
  storageProcess.join()
  flowCheckProcess.join()