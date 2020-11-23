import time
import io
import datetime
import dateutil.parser
from influxdb import InfluxDBClient
import matplotlib.pyplot as plt
import numpy as np
client = InfluxDBClient('localhost', 8086, 'waterrig', 'waterrigpw', 'watertestrig')

start = time.time()
while True:
  print("Fetching")
  result = client.query('SELECT mean(voltage0) as voltage0, mean(voltage1) as voltage1, mean(instantaneous) as instantaneous, mean(total) as total FROM adc, flow WHERE time >= now() - 5m GROUP BY time(1000ms) fill(null);')
  
  points = list(result.get_points(measurement="adc"))
  measurementPoints = list(result.get_points(measurement="flow"))

  if len(points) == 0:
    time.sleep(5)
    pass

  print("found {:} points".format(len(points)))

  print("Processing")
  times = np.array([dateutil.parser.isoparse(point["time"]).timestamp() for point in points])
  times = times - times[-1]
  
  transducerVoltage = np.array([point["voltage0"] for point in points])
  voltageDrop = np.array([(5.0 - point["voltage1"]) / 2 if not point["voltage1"] == None else None for point in points])

  ratio = np.array([(transducerVoltage[i]) / 5.0 if not transducerVoltage[i] == None else None for i in range(len(points))])
  pressure = np.array([1378951.46*((val - 0.1) / 0.8) / 1e5 if not val == None else None for val in ratio])

  instantaneous = np.array([point["instantaneous"] for point in measurementPoints])
  total = np.array([point["total"] for point in measurementPoints])

  fig = plt.figure(figsize=(12, 6))

  print("Drawing")

  uptime = time.time() - start

  plt.subplot(2,3,1)
  plt.plot(times, transducerVoltage)
  plt.xlabel("Time (s)")
  plt.ylabel("Voltage (V)")
  plt.grid()

  
  plt.subplot(2,3,2)
  plt.plot(times, voltageDrop)
  plt.xlabel("Time (s)")
  plt.ylabel("Voltage drop over cable (V)")
  plt.grid()


  plt.subplot(2,3,3)
  plt.plot(times, pressure)
  plt.xlabel("Time (s)")
  plt.ylabel("Pressure (bar)")
  plt.grid()


  plt.subplot(2,3,4)
  plt.plot(times, instantaneous)
  plt.xlabel("Time (s)")
  plt.ylabel("Flow (l/s)")
  plt.grid()

  
  plt.subplot(2,3,5)
  plt.plot(times, total)
  plt.xlabel("Time (s)")
  plt.ylabel("Total flow (l)")
  plt.grid()

  plt.subplot(2,3,6)
  plt.plot(pressure, instantaneous)
  plt.ylabel("Flow (l/s)")
  plt.xlabel("Pressure (bar)")
  plt.grid()

  plt.suptitle("{:.2f} seconds since startup".format(uptime))
  plt.tight_layout(pad=1.1, rect=(0, 0, 1, 0.95))
  

  print("Storing")
  
  with io.BytesIO() as buf:
    fig.savefig(buf, dpi=fig.dpi)
    plt.close()

    print("Saving")
    with open('/var/www/html/temp.png', "wb") as f:
      f.write(buf.getbuffer())
    