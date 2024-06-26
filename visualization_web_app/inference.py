# inference.py

import numpy as np
import datetime
import os
import matplotlib.pyplot as plt
import json
import config
import logging
import earth2mip.initial_conditions
import xarray
logger = logging.getLogger("inference")
logger.setLevel(logging.INFO)
# Set number of GPUs to use to 1
os.environ["WORLD_SIZE"] = "1"
# Set model registry as a local folder
model_registry = config.MODEL_REGISTRY_FOLDER
os.makedirs(model_registry, exist_ok=True)
os.environ["MODEL_REGISTRY"] = model_registry
print(f"MODEL_REGISTRY set to: {os.environ['MODEL_REGISTRY']}")

# Now import Earth-2 MIP
from earth2mip import registry, inference_ensemble
from earth2mip.initial_conditions import cds
from earth2mip.networks.fcnv2_sm import load as fcnv2_sm_load
from earth2mip.schema import EnsembleRun
from earth2mip.schema import Grid, PerturbationStrategy

def main(update_status):
    print("loading FCNv2 small model, this can take a bit")
    run_inference(config.CONFIG_SAMPLE_TEXT, update_status)

def parse_config(config_input):
    config_dict = json.loads(config_input)
    return config_dict

def run_inference(config_input, update_status):
    config_str = json.dumps(config_input)
    inference_ensemble.main(config_str, update_status)

def load_dataset_from_inference_output(config_dict):
    def open_ensemble(f, domain, chunks={"time": 1}):
        time = xarray.open_dataset(f).time
        root = xarray.open_dataset(f, decode_times=False)
        ds = xarray.open_dataset(f, chunks=chunks, group=domain)
        ds.attrs = root.attrs
        return ds.assign_coords(time=time)
    
    domains = config_dict["weather_event"]["domains"][0]["name"]
    ensemble_members = config_dict["ensemble_members"]
    output_path = config_dict["output_path"]
    ds = open_ensemble(os.path.join(output_path, "ensemble_out_0.nc"), domains)
    return ds

if __name__ == "__main__":
    main()
