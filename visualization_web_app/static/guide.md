# User Guide for Simulation Configuration

Welcome to the Simulation Configuration Interface. This guide will help you understand how to use the various UI elements to set up and run your simulations.

## UI Elements

### Ensemble Members
- **Description:** Number of ensemble members to use for the simulation.
- **Input:** A numeric value.
- **Default:** 2

### Simulation Length
- **Description:** Length of the simulation in days.
- **Input:** A numeric value.
- **Default:** 7
- **Minimum Value:** 1

### Start Time
- **Description:** Start time for the simulation.
- **Input:** A date and time picker.
- **Default:** 2023-07-15T00:00:00

### Diagnostics Channels
- **Description:** Select the diagnostics channels you want to include in the simulation.
- **Input:** A multi-select dropdown.
- **Default:** t2m, u10m, v10m, r50
- **Note:** The t2m channel will always be included.

### Region Selection
- **Description:** Select the region for the simulation.
- **Options:** 
  - Global
  - Country
  - Custom

#### Country Region
- **Description:** When 'Country' is selected, you can choose a specific country and region size.
- **Inputs:**
  - **Country:** A dropdown to select the country.
  - **Region Size:** A numeric input to specify the region size in degrees.

#### Custom Region
- **Description:** When 'Custom' is selected, you can specify custom coordinates and region size.
- **Inputs:**
  - **Longitude:** Longitude of the center of the region.
  - **Latitude:** Latitude of the center of the region.
  - **Region Size:** Region size in degrees.

### Skip Inference
- **Description:** Skip the inference step if checked.
- **Input:** A checkbox.
- **Default:** Checked

### Start Simulation Button
- **Description:** Start the simulation with the specified configuration.
- **Action:** Submits the form and starts the simulation.

### Terminal
- **Description:** Displays the current status of the simulation.
- **Output:** Text status messages.

## Instructions

1. **Configure the Simulation Parameters:**
   - Set the number of ensemble members.
   - Specify the simulation length.
   - Choose the start time for the simulation.

2. **Select Diagnostics Channels:**
   - Use the multi-select dropdown to choose the channels you want.
   - Ensure that the t2m channel is included (it will be automatically added if not selected).

3. **Choose the Region:**
   - Select 'Global' for a global simulation.
   - Select 'Country' to choose a specific country and set the region size.
   - Select 'Custom' to specify custom coordinates and region size.

4. **Skip Inference:**
   - Check the box if you want to skip the inference step.

5. **Start the Simulation:**
   - Click the 'Start Simulation' button to begin the simulation with the specified configuration.

6. **Monitor the Status:**
   - Check the terminal at the bottom of the interface for status updates.

## Additional Information

- The `Guide` button in the interface can be used to open and close this guide.
- Ensure all inputs are valid before starting the simulation to avoid errors.
- The simulation results can be viewed in the CesiumJS visualization interface.

For more detailed information, please refer to the project documentation.
