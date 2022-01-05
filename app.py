from flask import Flask
from flask import render_template, url_for, request
from time import sleep
import os
import logging 
from turbo_flask import Turbo
import threading

logging.basicConfig(level=logging.DEBUG)

temperature = 0
humidity = 0
turbocount = 0
glcount = 0
app = Flask(__name__)
turbo = Turbo(app)


@app.route("/", methods=['GET','POST'])
def index():
    global temperature
    global humidity
    global glcount

    if request.method == 'POST':
        glcount += 1
        # app.logger.info(request.form)  
        temperature = float(request.form.get('temp'))
        humidity = float(request.form.get('hum'))
        print()
        return render_template('base.html', temperature=temperature, humidity=humidity),

    print()
    return render_template('base.html', temperature=temperature, humidity=humidity)

@app.context_processor
def injectSensorData():
    global temperature
    global humidity
    # app.logger.info("injectSensorData ran. Pass gotlight = " + str(gotLight))
    return dict(temperature = float(temperature))

# Background updater thread that runs before 1st client connects
@app.before_first_request
def before_first_request():
    threading.Thread(target=update_sensor_data).start()

def update_sensor_data():
    global turbocount
    global glcount

    with app.app_context():    
        while True:
            sleep(4)
            app.logger.info("At turbo function #" + str(turbocount) + " now. It sees temperature " + "#" + str(glcount) +" = " + str(temperature))
            turbocount+=1
            turbo.push(turbo.replace(render_template('base.html'), 'base'))

if __name__ == '__main__':
    port = os.environ.get("PORT", 5000)              # Get port number of env at runtime, else use default port 5000
    app.run(debug=False, host='0.0.0.0', port=port)  # 0.0.0.0 port forwarding resolves the host IP address at runtime

