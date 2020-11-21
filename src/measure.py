from multiprocessing import Process, Queue

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

  channels = [chan0, chan1]

  while True:
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    for i in range(len(channels)):
      measurement = {
        "measurement": "adc",
        "tags": {
          "input": i,
        },
        "time": now,
        "fields": {
          "value": channels[i].value,
          "voltage": channels[i].voltage
        }
      }
      queue.put(measurement)

    time.sleep(0.05)

def storage(queue: Queue):
  import time
  from influxdb import InfluxDBClient
  client = InfluxDBClient('localhost', 8086, 'waterrig', 'waterrigpw', 'watertestrig')

  while True:
    batch = []
    while len(batch) < 100:
      batch.append(queue.get())

    client.write_points(batch)

if __name__ == '__main__':
  q = Queue()
  measurementProcess = Process(target=measurement, args=(q,))
  measurementProcess.start()
  storageProcess = Process(target=storage, args=(q,))
  storageProcess.start()
  measurementProcess.join()
  storageProcess.join()