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