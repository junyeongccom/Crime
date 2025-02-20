from flask import Flask, render_template
from com.junyeongc.models.crime_controller import CrimeController

app = Flask(__name__)
@app.route('/')
def index():
    crimecontroller = CrimeController() 
    crimecontroller.modeling('cctv_seoul.csv', 'crime_seoul.csv', 'pop_seoul.xls')
    return render_template('index.html')
