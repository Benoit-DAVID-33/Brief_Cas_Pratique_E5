from flask import Flask, render_template, request
from keras.models import load_model
import flask_monitoringdashboard as dashboard
from src.get_data import GetData
from src.utils import create_figure, prediction_from_model 
from functools import wraps
import time
from src.logging_config import configure_logging

app = Flask(__name__)

# Configurer le logging
configure_logging(app)

try:
    data_retriever = GetData(url="https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B")
    data = data_retriever()
    app.logger.info("Data retrieved successfully")
except Exception as e:
    app.logger.error(f"Failed to retrieve data: {e}")
    data = None

try:
    model = load_model('model.h5')
    app.logger.info("Model loaded successfully")
except Exception as e:
    app.logger.error(f"Failed to load model: {e}")
    model = None

def monitor_response_time(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        response = f(*args, **kwargs)
        duration = time.time() - start_time
        
        # Check if the duration exceeds the threshold
        if duration > 2:  # seuil de 2 secondes
            app.logger.warning(f"High response time: {duration} seconds for {request.path}")
        
        return response
    
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
@monitor_response_time
def index():
    if data is None or model is None:
        return "Error loading data or model", 500

    selected_hour = None
    fig_map = create_figure(data)
    graph_json = fig_map.to_json()

    if request.method == 'POST':
        selected_hour = request.form['hour']
        app.logger.info(f"Selected hour for prediction: {selected_hour}")

        cat_predict = prediction_from_model(model, selected_hour)
        color_pred_map = {0:["Prédiction : Libre", "green"], 1:["Prédiction : Dense", "orange"], 2:["Prédiction : Bloqué", "red"]}

        return render_template('index.html', graph_json=graph_json, text_pred=color_pred_map[cat_predict][0], color_pred=color_pred_map[cat_predict][1])

    return render_template('index.html', graph_json=graph_json)

# Ajouter le gestionnaire d'exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Exception occurred: {e}")
    return "Internal Server Error", 500

# Initialiser le tableau de bord
dashboard.config.enable_logging = True
dashboard.bind(app)
dashboard.config.monitor_level = 3

if __name__ == '__main__':
    app.run(debug=True)
