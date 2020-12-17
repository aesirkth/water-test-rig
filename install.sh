#!/bin/bash
cd /home/pi

if [ $1 != "skip-install" ]
then
  echo ""
  echo "Updating repositories"
  sudo apt-get update && sudo apt-get upgrade -y

  echo ""
  echo "Installing bash"
  sudo apt-get install bash -y

  echo ""
  echo "Installing Python3"
  sudo apt-get install python3-pip -y

  echo ""
  echo "Installing git"
  sudo apt-get install git -y

  echo ""
  echo "Installing InfluxDB"
  wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key    add -
  source /etc/os-release
  echo "deb https://repos.influxdata.com/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
  sudo apt-get update && sudo apt-get upgrade -y
  sudo apt install -y influxdb

  echo ""
  echo "Starting InfluxDB service"
  sudo systemctl unmask influxdb.service
  sudo systemctl start influxdb
  sudo systemctl enable influxdb.service
  sudo systemctl daemon-reload

  echo ""
  echo "Installing Nginx"
  sudo apt install -y nginx
  sudo chmod +755 -R /var/www/html

  INFLUX_COMMAND="create database watertestrig;
  use watertestrig;
  create user waterrig with password 'waterrigpw' with all privileges;
  grant all privileges on watertestrig to waterrig;
  create retention policy \"rawdata\" on \"watertestrig\" duration 24h replication 1 default;"
  influx -execute "$INFLUX_COMMAND"


  echo ""
  echo "Starting Nginx service"
  sudo systemctl start nginx
  sudo systemctl enable nginx
  sudo systemctl daemon-reload
fi

echo ""
echo "Setting Nginx configuration"

NGINX_CONFIG="user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
  worker_connections 768;
}

http {
  sendfile on;
  tcp_nopush on;
  tcp_nodelay on;
  keepalive_timeout 65;
  types_hash_max_size 2048;

  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
  ssl_prefer_server_ciphers on;

  access_log /var/log/nginx/access.log;
  error_log /var/log/nginx/error.log;

  gzip on;

  include /etc/nginx/conf.d/*.conf;
  include /etc/nginx/sites-enabled/*;
}"
sudo chmod +755 -R /etc/nginx
sudo chmod +755 /etc/nginx/nginx.conf
sudo chmod +755 /etc/nginx/sites-enabled/default
echo "$NGINX_CONFIG" | sudo tee /etc/nginx/nginx.conf > /dev/null


NGINX_SITE_CONFIG="server {
  listen 80 default_server;
  listen [::]:80 default_server;

  root /var/www/html;

  index index.html index.htm index.nginx-debian.html;

  etag off;
  
  server_name _;

  location / {
    try_files \$uri \$uri/ =404;

    add_header 'Access-Control-Allow-Origin' '*';
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
    add_header Cache-Control 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0';
  }
}"
echo "$NGINX_SITE_CONFIG" | sudo tee /etc/nginx/sites-enabled/default > /dev/null

sudo nginx -s reload
sudo systemctl start nginx
echo ""
echo "Cloning repository"

REPO_DIR=~/water-test-rig

if [ -d "$REPO_DIR" ]; then
  echo "Deleted existing repository" # delete if exists
  rm -rf $REPO_DIR
fi

git clone https://github.com/aesirkth/water-test-rig $REPO_DIR
cd $REPO_DIR
sudo chmod +755 -R /var/www/html
mkdir /var/www/html/lib/
cp ./src/client/index.html /var/www/html/
cp ./src/client/script.js /var/www/html/
cp ./src/client/style.css /var/www/html/
cp ./src/client/lib/plotly.min.js /var/www/html/lib/


echo ""
echo "Installing Python dependencies"
pip3 install adafruit-circuitpython-busdevice
pip3 install adafruit-circuitpython-mcp3xxx
pip3 install influxdb


echo ""
echo "Setting up default Influx database"

INFLUX_COMMAND="create database watertestrig;
use watertestrig;
create user waterrig with password 'waterrigpw' with all privileges;
grant all privileges on watertestrig to waterrig;
create retention policy \"rawdata\" on \"watertestrig\" duration 24h replication 1 default;"
influx -execute "$INFLUX_COMMAND"



MEASURE_DEAMON="[Unit]
Description=WaterTestRig Measure Script

[Service]
ExecStart=/usr/bin/python3 /home/pi/water-test-rig/src/measure.py
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target"

sudo touch /etc/systemd/system/waterTestRigMeasureDaemon.service
sudo chmod 777 /etc/systemd/system/waterTestRigMeasureDaemon.service
echo "$MEASURE_DEAMON" | sudo tee /etc/systemd/system/waterTestRigMeasureDaemon.service > /dev/null

sudo systemctl start waterTestRigMeasureDaemon.service
sudo systemctl enable waterTestRigMeasureDaemon.service
# sudo systemctl status waterTestRigMeasureDaemon.service

PROCESSING_DEAMON="[Unit]
Description=WaterTestRig Processing Script

[Service]
ExecStart=/usr/bin/python3 /home/pi/water-test-rig/src/processing.py
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target"

sudo touch /etc/systemd/system/waterTestRigProcessingDaemon.service
sudo chmod 777 /etc/systemd/system/waterTestRigProcessingDaemon.service
echo "$PROCESSING_DEAMON" | sudo tee /etc/systemd/system/waterTestRigProcessingDaemon.service > /dev/null

sudo systemctl start waterTestRigProcessingDaemon.service
sudo systemctl enable waterTestRigProcessingDaemon.service
# sudo systemctl status waterTestRigProcessingDaemon.service

echo ""
echo "Reloading Daemon"
sudo systemctl daemon-reload