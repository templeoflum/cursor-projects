from flask import Flask, render_template
from funnel_data import FunnelData

app = Flask(__name__)

@app.route('/')
def show_funnel():
    funnel = FunnelData.load('my_funnel.yaml')
    return render_template('funnel.html', funnel=funnel) 