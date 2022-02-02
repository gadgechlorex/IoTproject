from flask import Flask, render_template, request, redirect, make_response, Response
import random
import json
from random import random
from flask_sqlalchemy import SQLAlchemy
from time import sleep
import os
import logging 
from turbo_flask import Turbo
import threading
from datetime import datetime
from pytz import timezone
import time

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI']='postgresql://hixbecdmrrcvyn:3c2759024c0bc8cea6c55e6c4d72996a76391e279c92e14d14c721aab54b2a23@ec2-34-232-25-204.compute-1.amazonaws.com:5432/d7k7vrv431ico3'

logging.basicConfig(level=logging.DEBUG)
temperature = 0
humidity = 0
turbocount = 0
glcount = 0

turbo = Turbo(app)

db=SQLAlchemy(app)

class Customers(db.Model):
  __tablename__='customer'
  id=db.Column(db.Integer,primary_key=True)
  name=db.Column(db.String(255), nullable=False)
  email=db.Column(db.String(255), nullable=False)
  readingss = db.relationship('Reading', backref=db.backref('customer',lazy=True))
	
  def __init__(self,name,email):
    self.name=name
    self.email=email

class Reading(db.Model):
  __tablename__='readings'
  id=db.Column(db.Integer,primary_key=True)
  temperature=db.Column(db.Float(2), nullable=False)
  humidity=db.Column(db.Float(2), nullable=False)
  reading_time=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  customer_id=db.Column(db.Integer,db.ForeignKey('customer.id'),nullable=False)
    
  def __init__(self,temperature,humidity,reading_time,customer_id):
    self.temperature = temperature
    self.humidity = humidity
    self.reading_time = reading_time
    self.customer_id = customer_id


#Starting page

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/submit', methods=['GET','POST'])
def submit():
  name= request.form['name']
  email=request.form['email']
  
  user = Customers(name,email)
  db.session.add(user)
  db.session.commit()

  return redirect('/log_Data')

@app.route('/log_Data', methods=['GET','POST'])
def log_Data():
    global temperature
    global humidity
    global time

    if request.method == 'POST':
        # app.logger.info(request.form)  
        temperature = float(request.form.get('temp'))
        humidity = float(request.form.get('hum'))
        newlog = Reading(
        temperature = float(request.form.get('temp')), 
        humidity = float(request.form.get('hum')), 
        reading_time = datetime.now(tz=timezone('Asia/Kuala_Lumpur')),
        customer_id = 1
        )
        
        db.session.add(newlog)
        db.session.commit()        
	
        ##return "data logged"
        
    return render_template('base.html', temperature=temperature, humidity=humidity,time=time)
    
    
@app.route('/data', methods=["GET", "POST"])
def data():    
    if request.method == 'GET':
        Temperature = temperature
        Humidity = humidity	
        data = [time() * 1000, Temperature, Humidity]

        response = make_response(json.dumps(data))

        response.content_type = 'application/json'

        return response    

@app.route('/temp-data')
def temp_data():
    def generate_temp_data():
        while True:
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': temperature})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_temp_data(), mimetype='text/event-stream')     

@app.route('/hum-data')
def hum_data():
    def generate_hum_data():
        while True:
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': humidity})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_hum_data(), mimetype='text/event-stream')     



#-----------------------------------------------------------------------

@app.context_processor
def injectSensorData():
    global temperature
    global humidity    
        
    return dict(
    temperature = float(temperature), 
    humidity = float(humidity)
    )

#----------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Background updater thread that runs before 1st client connects
@app.before_first_request
def create_tables():
    db.create_all()

def before_first_request():
    threading.Thread(target=update_sensor_data).start()

def update_sensor_data():
    with app.app_context():    
        while True:
            sleep(4)
            turbo.push(turbo.replace(render_template('base.html'), 'base'))
            
#-----------------------------------------------------------------------

if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)# Get port number of env at runtime, else use default port 5000
    app.run(debug=True, host='0.0.0.0', port=port)  # 0.0.0.0 port forwarding resolves the host IP address at runtime
