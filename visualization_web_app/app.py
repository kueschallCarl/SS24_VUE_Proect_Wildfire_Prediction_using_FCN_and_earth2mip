import numpy as np
from flask import Flask, jsonify, send_from_directory, request, session
import config
import inference
import logging
import pandas as pd

logger = logging.getLogger("inference")
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.secret_key = '032849783209458u092509234850809'
inference_status = {'status': 'idle'}

country_coords = pd.read_csv('static/country-coord.csv')
country_coords.set_index('country', inplace=True)

def calculate_wildfire_risk(avg_t2m_data, avg_u10m_data, avg_v10m_data, avg_r50_data):
    # Automatically normalize temperature data
    min_temp = np.min(avg_t2m_data)
    max_temp = np.max(avg_t2m_data)
    normalized_temp = (avg_t2m_data - min_temp) / (max_temp - min_temp)
    
    # Automatically normalize wind speed
    wind_speed = np.sqrt(avg_u10m_data**2 + avg_v10m_data**2)
    min_wind = np.min(wind_speed)
    max_wind = np.max(wind_speed)
    normalized_wind = (wind_speed - min_wind) / (max_wind - min_wind)
    
    # Normalize r50_data inversely, since higher values indicate lower humidity
    normalized_r50 = (avg_r50_data - np.min(avg_r50_data)) / (np.max(avg_r50_data) - np.min(avg_r50_data))
    
    # Calculate risks based on normalized and transformed values using exponential function
    temp_risk = np.exp((normalized_temp - 0.5) * 2)  # Emphasize high temperatures
    wind_risk = np.exp((normalized_wind - 0.5) * 2)  # Emphasize high wind speeds
    dry_risk = np.exp((normalized_r50 - 0.5) * 2)  # Emphasize low humidity
    
    # Weightings for each risk component
    temp_weight = 0.8
    wind_weight = 0.1
    dry_weight = 0.1
    
    # Calculate wildfire risk for each point
    wildfire_risk = (temp_risk * temp_weight + wind_risk * wind_weight + dry_risk * dry_weight)
    
    # Normalize the final wildfire risk to be between 0 and 1
    wildfire_risk = (wildfire_risk - np.min(wildfire_risk)) / (np.max(wildfire_risk) - np.min(wildfire_risk))
    return wildfire_risk * 100

def preprocess_xarray_data(ds, channel, ensemble_member_index=0, region_select="global", longitude=None, latitude=None, region_size=0.5, time_index=0, max_points=150000, n_days=7):
    lons = ds.lon.values
    lats = ds.lat.values
    time_steps = ds[channel].shape[1]
    if time_index >= time_steps:
        raise IndexError(f"Time index {time_index} is out of bounds for available time steps {time_steps}")

    data = ds[channel][ensemble_member_index, time_index].values
    if channel == "t2m":
        data = data - 273.15

    lon_grid, lat_grid = np.meshgrid(lons, lats)
    lon_grid_flat = lon_grid.flatten()
    lat_grid_flat = lat_grid.flatten()
    data_flat = data.flatten()
    # Calculate wildfire risk for all datapoints
    # Calculate wildfire risk for all datapoints
    if time_index == 0:
        t2m_data = ds.t2m[ensemble_member_index, time_index:time_index+1, :, :].values
        u10m_data = ds.u10m[ensemble_member_index, time_index:time_index+1, :, :].values
        v10m_data = ds.v10m[ensemble_member_index, time_index:time_index+1, :, :].values
        r50_data = ds.r50[ensemble_member_index, time_index:time_index+1, :, :].values
    else:
        start_index = max(0, time_index - n_days)
        t2m_data = ds.t2m[ensemble_member_index, start_index:time_index, :, :].values
        u10m_data = ds.u10m[ensemble_member_index, start_index:time_index, :, :].values
        v10m_data = ds.v10m[ensemble_member_index, start_index:time_index, :, :].values
        r50_data = ds.r50[ensemble_member_index, start_index:time_index, :, :].values
        print(f"start_index: {start_index}, time index: {time_index}")

    if region_select == "country" or region_select == "custom":
        mask = (lat_grid_flat >= latitude - region_size / 2) & (lat_grid_flat <= latitude + region_size / 2) & \
               (lon_grid_flat >= longitude - region_size / 2) & (lon_grid_flat <= longitude + region_size / 2)
        # Apply mask to each time step
        t2m_data = t2m_data[:, mask.reshape(lat_grid.shape)]
        u10m_data = u10m_data[:, mask.reshape(lat_grid.shape)]
        v10m_data = v10m_data[:, mask.reshape(lat_grid.shape)]
        r50_data = r50_data[:, mask.reshape(lat_grid.shape)]

        lon_grid_flat = lon_grid_flat[mask]
        lat_grid_flat = lat_grid_flat[mask]
        data_flat = data_flat[mask]

    avg_t2m_data = np.mean(t2m_data, axis=0)
    avg_u10m_data = np.mean(u10m_data, axis=0)
    avg_v10m_data = np.mean(v10m_data, axis=0)
    avg_r50_data = np.mean(r50_data, axis=0)
    
    wildfire_risk = calculate_wildfire_risk(avg_t2m_data, avg_u10m_data, avg_v10m_data, avg_r50_data)
    wildfire_risk_flat = wildfire_risk.flatten()

    total_points = lon_grid_flat.size
    step = max(1, int(np.ceil(total_points / max_points)))

    downsampled_indices = np.arange(0, total_points, step)

    # Prepare downsampled data
    downsampled_lons = lon_grid_flat[downsampled_indices]
    downsampled_lats = lat_grid_flat[downsampled_indices]
    downsampled_values = data_flat[downsampled_indices]

    # Downsample wildfire risk
    downsampled_wildfire_risk = wildfire_risk_flat[downsampled_indices]

    data_json = {
        'lons': downsampled_lons.tolist(),
        'lats': downsampled_lats.tolist(),
        'values': downsampled_values.tolist(),
        'wildfire_risk': downsampled_wildfire_risk.tolist()
    }

    #print(data_json['wildfire_risk'])

    return data_json

@app.route('/data/<region_select>')
def data(region_select):
    custom_region_data = session.get('custom_region_data')
    longitude = None
    latitude = None
    region_size = 1.0
    time_index = int(request.args.get('time', 0))
    ensemble_member_index = int(request.args.get('ensemble', 0))
    channel = request.args.get('channel', 't2m')

    if region_select == "custom" or region_select == "country":
        longitude = custom_region_data['longitude']
        latitude = custom_region_data['latitude']
        region_size = custom_region_data['region_size']
    
    config_dict = session.get('config_dict', {})
    ds = inference.load_dataset_from_inference_output(config_dict=config_dict)
    ds_json_ready = preprocess_xarray_data(ds, channel, ensemble_member_index, region_select, longitude, latitude, region_size, time_index)

    return jsonify(ds_json_ready)

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    data = request.get_json()
    config_text = data['configText']
    region_select = data['regionSelect']
    skip_inference = data['skipInference']
    longitude = None
    latitude = None
    region_size = None
    channel_to_modify = data.get('channelToModify')
    modulating_factor = data.get('modulatingFactor')
    logger.info(f"channel to modify: {channel_to_modify}")
    logger.info(f"modulating_factor: {modulating_factor}")
    if region_select == 'custom':
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        region_size = data.get('regionSize')
        session['custom_region_data'] = {
            'longitude': longitude,
            'latitude': latitude,
            'region_size': region_size
        }
    elif region_select == 'country':
        country = data.get('country')
        if country in country_coords.index:
            longitude = country_coords.at[country, 'lon']
            latitude = country_coords.at[country, 'lat']
            region_size = data.get('regionSize')
            session['custom_region_data'] = {
                'longitude': longitude,
                'latitude': latitude,
                'region_size': region_size
            }
        else:
            return jsonify({'error': 'Country not found in the CSV file'}), 400

    config_dict = inference.parse_config(config_text)
    config_dict['channel_to_modify'] = channel_to_modify
    config_dict['modulating_factor'] = modulating_factor
    session['config_dict'] = config_dict

    if not skip_inference:
        inference_status['status'] = 'Inference started, this can take a minute...'
        logger.info("Inference started")
        inference.run_inference(config_dict)
        logger.info("Inference completed")
        inference_status['status'] = 'Inference completed'

    ds = inference.load_dataset_from_inference_output(config_dict=config_dict)

    return '', 200

@app.route('/get_status')
def get_status():
    return jsonify(inference_status)

@app.route('/get_config')
def get_config():
    config_dict = session.get('config_dict', {})
    return jsonify(config_dict)

@app.route('/cesium') 
def cesium():
    return send_from_directory('', 'cesium.html')

@app.route('/geojson/<path:filename>')
def geojson(filename):
    return send_from_directory('geojson', filename)
@app.route('/reset_status', methods=['POST'])
def reset_status():
    inference_status['status'] = 'idle'
    return '', 200
@app.route('/')
def index():
    return send_from_directory('', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
