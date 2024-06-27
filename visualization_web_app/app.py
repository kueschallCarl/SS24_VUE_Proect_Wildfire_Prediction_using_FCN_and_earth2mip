# app.py

import numpy as np
from flask import Flask, jsonify, send_from_directory, request, session
import config
import inference
import logging
import pandas as pd
import copy

logger = logging.getLogger("inference")
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.secret_key = '032849783209458u092509234850809'
inference_status = {'status': 'idle'}

country_coords = pd.read_csv('static/country-coord.csv')
country_coords.set_index('country', inplace=True)

def calculate_wildfire_risk(avg_t2m_data, avg_u10m_data, avg_v10m_data, avg_r50_data):
    # Calculate wind speed from u and v components
    wind_speed = np.sqrt(avg_u10m_data**2 + avg_v10m_data**2)

    # Calculate risks based on raw values using exponential function
    temp_risk = np.exp((avg_t2m_data - 273.15) / 10)  # Scale temperature (converted to Celsius) appropriately
    wind_risk = np.exp(wind_speed / 10)  # Scale wind speed appropriately
    dry_risk = np.exp((100 - avg_r50_data) / 10)  # Inverse scaling for humidity

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

    return data_json

def compute_and_add_deltas(ds_json_ready, ds_unmodulated_json_ready):
    # Ensure both datasets have the same structure
    if set(ds_json_ready.keys()) != set(ds_unmodulated_json_ready.keys()):
        raise ValueError("Modified and unmodified datasets have different structures")

    # Create a new dictionary to hold the deltas
    deltas_dict = {}
    logger.info(f"WATCH HERE | values before computing delta for modified: {ds_json_ready['values'][:5]}")
    logger.info(f"WATCH HERE | values before computing delta for unmodified: {ds_unmodulated_json_ready['values'][:5]}")
    for key in ds_json_ready.keys():
        if isinstance(ds_json_ready[key], list) and isinstance(ds_unmodulated_json_ready[key], list):
            if len(ds_json_ready[key]) != len(ds_unmodulated_json_ready[key]):
                raise ValueError(f"Length mismatch for key {key}")
        
            # Compute deltas
            if key == "values" or key == "wildfire_risk":
                deltas = [modified - unmodified for modified, unmodified in zip(ds_json_ready[key], ds_unmodulated_json_ready[key])]
                # Add deltas to the new dictionary
                deltas_dict[f"{key}_delta"] = deltas

    # Merge the deltas dictionary back into the original dictionary
    ds_json_ready.update(deltas_dict)
    return ds_json_ready


@app.route('/data/<region_select>')
def data(region_select):
    custom_region_data = session.get('custom_region_data')
    longitude = None
    latitude = None
    region_size = 1.0
    time_index = int(request.args.get('time', 0))
    ensemble_member_index = int(request.args.get('ensemble', 0))
    channel = request.args.get('channel', 't2m')

    if region_select in ["custom", "country"]:
        longitude = custom_region_data['longitude']
        latitude = custom_region_data['latitude']
        region_size = custom_region_data['region_size']
    
    config_dict = session.get('config_dict', {})
    ds = session.get('ds')
    
    logger.info(f"WATCH HERE:config_dict {config_dict}")
    
    ds = inference.load_dataset_from_inference_output(config_dict=config_dict)
    ds_json_ready = preprocess_xarray_data(ds, channel, ensemble_member_index, region_select, longitude, latitude, region_size, time_index)
    
    if config_dict['modulating_factor'] != 1.0:
        logger.info(f"WATCH HERE: Running both inferences, this should work...")
        
        config_dict_unmodulated = copy.deepcopy(config_dict)
        config_dict_unmodulated['modulating_factor'] = 1.0
        logger.info(f"WATCH HERE:confict_dict_unmodulated {config_dict_unmodulated}")
        
        ds_unmodulated = inference.load_dataset_from_inference_output(config_dict=config_dict_unmodulated)
        ds_unmodulated_json_ready = preprocess_xarray_data(ds_unmodulated, channel, ensemble_member_index, region_select, longitude, latitude, region_size, time_index)
    else:
        logger.info(f"WATCH HERE: Setting ds_unmodulated_json_ready = ds_json_ready haha")
        ds_unmodulated_json_ready = ds_json_ready

    ds_json_ready_with_deltas = compute_and_add_deltas(ds_json_ready, ds_unmodulated_json_ready)
    #logger.info(f"WATCH HERE: {ds_json_ready_with_deltas.keys()}")
    #logger.info(f"WATCH HERE | Wildfire Risk delta values: {ds_json_ready_with_deltas['wildfire_risk_delta']}")
    logger.info(f"WATCH HERE | Value delta values for channel {channel}: {ds_json_ready_with_deltas['values_delta']}")

    return jsonify(ds_json_ready_with_deltas)

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

    def update_status(message):
        inference_status['status'] = message
        logger.info(message)
    
    if not skip_inference:
    
        if modulating_factor != 1.0:
            update_status('Inference started for unmodified data, this can take a minute...')
            config_dict_unmodulated = copy.deepcopy(config_dict)
            config_dict_unmodulated['modulating_factor'] = 1.0
            logger.info("Inference started for unmodified data")
            inference.run_inference(config_dict_unmodulated, update_status)
            logger.info("Inference completed")
            update_status('Inference completed for unmodified data')
            

        update_status('Inference started for modified data, this can take a minute...')
        logger.info("Inference started for modified data")
        inference.run_inference(config_dict, update_status)
        logger.info("Inference completed")
        update_status('Inference completed for modified data')

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
