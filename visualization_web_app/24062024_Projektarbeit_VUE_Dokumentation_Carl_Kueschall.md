# SS24 Project VUE: Visualizing the Prediction of Wildfires Globally Using FourCastNet and Earth2Mip
- OTH Amberg-Weiden
- Author
    - Carl Kueschall
- Supervisor
    - Prof. Peterhaensel
- Class
    - SS2024 | Visualization and Explanation-Components

## Abstract
This project, developed as part of the "Visualizations and Explanation-Components" class at the OTH Amberg-Weiden, enables the prediction of wildfires under real, as well as manipulated initial conditions, across the entire globe and in a time-spectrum between 1940 and the present, using the FourCastNetv2_small forecasting model. More specifically, leveraging the [Cesium.ion](https://cesium.com/platform/cesium-ion/) web-based visualization framework, this project visualizes the outputs of the forecasting model in an approachable manner, enabling an intuitive understanding of weather-conditions and -extremes, at a glance.
## Features
### Presentation on YouTube
[YouTube Presentation (in German)](youtube.com)
### Global Wildfire Prediction
The core feature of this project is the ability to predict wildfires globally using the FourCastNetv2_small forecasting model. The model leverages historical weather data and can simulate future conditions, offering a time-spectrum from 1940 to the present. The predictions account for real as well as manipulated initial conditions to provide comprehensive forecasts.

### Interactive Web-Based Visualization
The project uses the [Cesium.ion](https://cesium.com/platform/cesium-ion/) framework to visualize prediction data. This interactive, web-based visualization allows users to explore weather conditions and wildfire risks in an intuitive, user-friendly manner. Users can navigate a 3D globe, view different weather parameters, and observe predicted wildfire risks.

### Customizable Simulation Configuration
Users can customize their simulations via a web interface provided by the `index.html` file. This includes setting parameters such as:
- The number of ensemble members
- Simulation length
- Start time
- Diagnostics channels to monitor (e.g., temperature, wind speed)
- Regions of interest (global, specific countries, or custom-defined regions)
- Modulating factors to adjust weather conditions

### Real-Time Data Interaction
The visualization framework supports real-time interaction with the data. Users can:
- Select different time frames to view the progression of weather conditions and wildfire risks.
- Change the channel being visualized (e.g., temperature, wind speed).
- Toggle display options such as wildfire markers and detailed data points.
- Use a time slider to move through the simulation timeline.

### Wildfire Risk Calculation
The application includes a detailed method for calculating wildfire risks based on normalized temperature, wind speed, and humidity data. This calculation is integral to the visualization, highlighting areas of high wildfire risk based on real-time weather conditions.


## Installation and Setup

### Step 1 | Earth2Mip Repository
First of all, [my fork of the earth2mip repository](https://github.com/kueschallCarl/earth2mip) has to be cloned to your location of choice using git. I recommend using Linux or WSL 2.0, in combination with miniConda for the installation of this project.

### Step 2 | Downloading and Inserting the FCNv2_small Model
**Option A**: Install model via Modulus Framework using Docker
- [Guide 1a: Downloading the Model (Docker Option)](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/modulus/models/modulus_fcnv2_sm)

**Option B**: Install model by manually downloading and extracting zip-file
- [Guide 1b: Downloading the Model (Zip File)](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/modulus/models/modulus_fcnv2_sm/files) 
- Ensure that the following files are placed inside the 'earth2mip/visualization_web_app/models/fcnv2_sm' directory:
    - global_means.npy
    - global_stds.npy
    - metadata.json
    - weights.tar

**Ensure that the MODEL_REGISTRY_FOLDER constant inside config.py is set correctly to 'YOUR_PARENT_DIRS/earth2mip/visualization_web_app/models/'**

### Step 3 | Build eart2mip and install dependencies

#### Build earth2mip
Navigate to the directory that contains the 'setup.py' file, which should be 'earth2mip/setup.py'. Then in the terminal, using a python version that satisfies earth2mip's requirements (3.10 | 3.11 | 3.12 as of the 24th of June 2024), run 
```bash
pip install .
```
This should build the earth2mip package inside the earth2mip repository. 

#### Install additional project-specific dependencies
Navigate to "earth2mip/visualization_web_app" and in a terminal run

```bash
pip install -r requirements.txt
```

### Step 4 | Sign up without cost at Cesium.ion and set your access token
Having signed up at [Cesium.com](https://cesium.com/platform/cesium-ion/), navigate to your [Cesium.ion account access tokens](https://ion.cesium.com/tokens?page=1), create a token and copy it into the 'cesium.html' file at line 165.
```javascript
        Cesium.Ion.defaultAccessToken = '<YOUR_TOKEN>';
```



## References
### Guides / Tutorials
- [Guide 1a: Downloading the Model (Docker Option)](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/modulus/models/modulus_fcnv2_sm) 
- [Guide 1b: Downloading the Model (Zip File)](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/modulus/models/modulus_fcnv2_sm/files) 
- [Guide 2: Installing earth2mip](https://github.com/NVIDIA/earth2mip)
- [Guide 3: Installing Docker](https://docs.docker.com/engine/install/)
### Literature
- [Spherical Fourier Neural Operators: Learning Stable Dynamics on the Sphere](https://arxiv.org/abs/2306.03838) 
- [FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators](https://arxiv.org/abs/2202.11214) 
- [Spherical Fourier Neural Operators: Learning Stable Dynamics on the Sphere](https://arxiv.orgsabs/2306.03838) 
- [Climate reanalysis](https://climate.copernicus.eu/climate-reanalysis) 
### Resources
- [ERA5 hourly data on single levels from 1940 to present](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview) 
- [My fork of the earth2mip repository](https://github.com/kueschallCarl/earth2mip)
- [Cesium.ion](https://cesium.com/platform/cesium-ion/)