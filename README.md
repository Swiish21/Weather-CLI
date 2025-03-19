# Weather CLI

A command-line interface for getting weather forecasts using the OpenWeatherMap API.

## Features
- Get current weather for any location
- Multiple location support
- Detailed weather information including temperature, humidity, and wind speed
- Weather alerts for severe conditions
- Beautiful terminal output using Rich

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Get an API key from [OpenWeatherMap](https://openweathermap.org/api)
4. Create a `.env` file in the project root and add your API key:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

## Usage

```bash
# Get current weather for a location
python weather_cli.py current "London, UK"

# Get weather forecast for a location
python weather_cli.py forecast "New York, US"

# Add a location to favorites
python weather_cli.py add-favorite "Paris, FR"

# Get weather for all favorite locations
python weather_cli.py favorites

# Get weather alerts for a location
python weather_cli.py alerts "Tokyo, JP"
``` 