# VUE Project Wildfire Prediction and Visualization using FourCastNet

## Simulation Configuration Guide

This guide will help you set up the simulation for predicting and visualizing wildfire risks using FourCastNet. Follow the steps below:

### Step-by-Step Configuration

<ol>
  <li>Number of Times Weather Conditions should be Predicted:
    <ul>
      <li>Number of times the weather prediction simulation will run.</li>
      <li><strong>Example:</strong> Enter <code>2</code>. This will run the prediction 2 times and provide a second 'opinion'.</li>
    </ul>
  </li>

  <li>Number of Days to Forecast Weather:
    <ul>
      <li>The duration in days for which the weather will be forecasted.</li>
      <li><strong>Example:</strong> Enter <code>7</code>. This will forecast 7 days into the future</li>
    </ul>
  </li>

  <li>Starting-Point in Time for Weather Forecasting:
    <ul>
      <li>The initial time from which the weather forecast simulation will start.</li>
      <li><strong>Example:</strong> Enter <code>2023-07-15T00:00:00</code>. This causes the forecast to start on the 15th of July 2023.</li>
    </ul>
  </li>

  <li>Parameter to Modify:
    <ul>
      <li>Select the weather parameter to be modified in the simulation.</li>
      <li><strong>Options:</strong>
        <ul>
          <li><code>Temperature</code></li>
          <li><code>Wind Speed West to East</code></li>
          <li><code>Wind Speed South to North</code></li>
          <li><code>Humidity</code></li>
        </ul>
      </li>
    </ul>
  </li>

  <li>Percentage to Modify Parameter by Across the Globe at Starting-Time:
    <ul>
      <li>The percentage by which the selected parameter will be adjusted globally at the start of the simulation.</li>
      <li><strong>Example:</strong> Enter <code>10</code> for a 10% modification. In other words: 100% + 10% = 110% -> 25°C * 1.1 = 27.5°C</li>
    </ul>
  </li>

  <li>Select Region on the Globe to Visualize:
    <ul>
      <li>Select the geographical region for the simulation.</li>
      <li><strong>Options:</strong>
        <ul>
          <li><code>Global</code></li>
          <li><code>Country</code></li>
          <li><code>Custom</code></li>
        </ul>
      </li>
    </ul>
  </li>
</ol>

### Additional Configuration for Selected Regions

- **Country:**
  <ol>
    <li>Select Country:
      <ul>
        <li>Select a specific country for the simulation. The center coordinate of the selected country will be the center of the visualized data. The breadth and width of the visualized area from that point onward depends on the choice of 'Region Size</li>
      </ul>
    </li>
    <li>Region Size (degrees):
      <ul>
        <li>Specify the size of the region around the selected country.</li>
        <li><strong>Example:</strong> Enter <code>10</code>. This will visualize a data in 10 degrees latitude and longitude around the center of the selected country or custom coordinate, in a square block.</li>
      </ul>
    </li>
  </ol>

- **Custom:**
  <ol>
    <li>Longitude:
      <ul>
        <li>Enter the value of longitude for the custom location.</li>
      </ul>
    </li>
    <li>Latitude:
      <ul>
        <li>Enter the value of latitude for the custom location.</li>
      </ul>
    </li>
    <li>Region Size (degrees):
      <ul>
        <li>Specify the size of the custom region.</li>
        <li><strong>Example:</strong> Enter <code>10</code>. This will visualize a data in 10 degrees latitude and longitude around the center of the selected country or custom coordinate, in a square block.</li>
      </ul>
    </li>
  </ol>

### Skip Inference
- Check this box if you want to skip running the model from scratch and use existing results. The project stores prediction output locally once performed once. This data will be detected automatically meaning that you don't have to run the model twice for a given configuration. <br>
**IMPORTANT**: Changing the starting date-time for the forecast or the percentage to modify parameter by, the model has to be run again.

### Example Configuration

To help you get started, here's an example setup for predicting temperature changes over the United States:

1. **Number of Times Weather Conditions should be Predicted:** `3`
2. **Number of Days to Forecast Weather:** `5`
3. **Starting-Point in Time for Weather Forecasting:** `2023-07-15T00:00:00`
4. **Parameter to Modify:** `Temperature`
5. **Percentage to Modify Parameter by Across the Globe at Starting-Time:** `5`
6. **Select Region on the Globe to Visualize:** `Country`
7. **Select Country:** `United States`
8. **Region Size (degrees):** `15`

With this configuration, you will run a simulation three times over five days starting from July 15, 2023, focusing on temperature changes in the United States, adjusting the temperature by 5%.

Follow these steps, and you will be able to set up and run your simulation successfully.
