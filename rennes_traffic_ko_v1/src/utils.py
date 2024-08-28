# utils.py
import plotly.express as px
import numpy as np
import logging

# Configurer un logger temporaire
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Ajustez le niveau si nécessaire
handler = logging.StreamHandler()  # Utiliser un stream handler pour afficher dans la console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def create_figure(data):
    fig_map = px.scatter_mapbox(
            data,
            title="Traffic en temps réel",
            color="traffic",
            lat="lat",
            lon="lon",
            color_discrete_map={'freeFlow':'green', 'heavy':'orange', 'congested':'red'},
            zoom=10,
            height=500,
            mapbox_style="carto-positron"
    )
    return fig_map

def prediction_from_model(model, hour_to_predict):
    try:
        input_pred = np.array([0]*24)
        input_pred[int(hour_to_predict)] = 1

        cat_predict = np.argmax(model.predict(np.array([input_pred])))

        return cat_predict
    except Exception as e:
        logger.error(f"Model prediction failed: {e}")
        return -1  # valeur par défaut pour indiquer une erreur
