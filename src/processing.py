import time
import os
import math
import datetime
import dateutil.parser

from influxdb import InfluxDBClient

client = InfluxDBClient('localhost', 8086, 'waterrig', 'waterrigpw', 'watertestrig')

start = time.time()
while True:
  for ranges in [("60m", "1s")]:
    fullRange, interval = ranges
    
    filename = '/var/www/html/data_{:}.txt'.format(fullRange)
    tmp_filename = '{:}.tmp'.format(filename)

    print("Fetching {:} with step {:}".format(fullRange, interval))
    result = client.query('SELECT mean(voltage0) as voltage0, mean(voltage1) as voltage1, mean(instantaneous) as instantaneous, mean(total) as total FROM adc, flow WHERE time >= now() - {:} GROUP BY time({:}) fill(null);'.format(fullRange, interval))
    
    points = list(result.get_points(measurement="adc"))
    measurementPoints = list(result.get_points(measurement="flow"))

    if len(points) == 0:
      time.sleep(5)
      continue

    print("found {:} points".format(len(points)))

    import csv
    with open(tmp_filename, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
      lastTime = dateutil.parser.isoparse(points[len(points) - 1]["time"]).timestamp()
      for i in range(len(points)):
        currentTime = dateutil.parser.isoparse(points[i]["time"]).timestamp() - lastTime
        voltage0 = points[i]["voltage0"]
        voltage1 = points[i]["voltage1"]

        instantaneous = measurementPoints[i]["instantaneous"]
        total = measurementPoints[i]["total"]

        writer.writerow([
          currentTime, voltage0, voltage1, instantaneous, total
        ])

    os.rename(tmp_filename, filename)
    

  continue # Don't plot?

  print("Processing")
  import numpy as np
  times = np.array([dateutil.parser.isoparse(point["time"]).timestamp() for point in points])
  times = times - times[-1]
  
  transducerVoltage = np.array([point["voltage0"] for point in points])
  voltageDrop = np.array([(5.0 - point["voltage1"]) / 2 if not point["voltage1"] == None else None for point in points])

  baseLevel = 0.5125
  ratio = np.array([(transducerVoltage[i] - baseLevel) / 4.0 if not transducerVoltage[i] == None else None for i in range(len(points))])

  maxPressure = 1.2e6 # 1378951.46
  pressure = np.array([maxPressure*val / 1e5 if not val == None else None for val in ratio])

  instantaneous = np.array([point["instantaneous"] if not point["instantaneous"] == None else None for point in measurementPoints])
  total = np.array([point["total"] if not point["total"] == None else None for point in measurementPoints])

  print("Drawing")
  import matplotlib.pyplot as plt
  import io
  fig = plt.figure(figsize=(16, 8))

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

  waterDensity = 997

  massFlow = np.array([point / 1000 * waterDensity if not point == None else None for point in instantaneous])

  plt.subplot(2,3,6)
  plt.plot(pressure, massFlow, '.')
  plt.ylabel("Flow (kg/s)")
  plt.xlabel("Pressure (bar)")
  plt.grid()

  pressureWithoutNone = [point if not point == None else 0 for point in pressure]
  pressures = np.linspace(0, np.max(pressureWithoutNone), 50)
  legends = ("Measured",)
  for cD in [0.25, 0.5, 0.75, 1]:
    numHoles = 13
    holeDiameterMm = 1.5
    area = numHoles * pow((holeDiameterMm/1000.0)/2.0, 2.0) * math.pi

    theoretical = cD * area * np.sqrt(2 * waterDensity * pressures * 1e5)

    plt.plot(pressures, theoretical, '--')
    legends = (*legends, "Cd = {:.2f}".format(cD))
  plt.legend(legends)
    

  plt.suptitle("{:.2f} seconds since startup".format(uptime))
  plt.tight_layout(pad=1.1, rect=(0, 0, 1, 0.95))
  

  print("Storing")
  
  with io.BytesIO() as buf:
    fig.savefig(buf, dpi=fig.dpi)
    plt.close()

    print("Saving")
    with open('/var/www/html/temp.png', "wb") as f:
      f.write(buf.getbuffer())
    