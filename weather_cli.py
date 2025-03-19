#!/usr/bin/env python3
import os
import json
import click
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from dotenv import load_dotenv
from typing import Dict, List, Optional
from datetime import datetime

# Initialize Rich console
console = Console()

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')
BASE_URL = "http://api.openweathermap.org/data/2.5"
FAVORITES_FILE = "favorites.json"

class WeatherAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_location_coords(self, location: str) -> tuple:
        """Get coordinates for a location name."""
        url = f"http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": location,
            "limit": 1,
            "appid": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise click.ClickException(f"Location '{location}' not found")
                
            return data[0]["lat"], data[0]["lon"]
            
        except requests.RequestException as e:
            raise click.ClickException(f"Error fetching location data: {str(e)}")

    def get_current_weather(self, location: str) -> Dict:
        """Get current weather for a location."""
        lat, lon = self.get_location_coords(location)
        
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/weather", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise click.ClickException(f"Error fetching weather data: {str(e)}")

    def get_forecast(self, location: str) -> Dict:
        """Get 5-day forecast for a location."""
        lat, lon = self.get_location_coords(location)
        
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/forecast", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise click.ClickException(f"Error fetching forecast data: {str(e)}")

    def get_alerts(self, location: str) -> Dict:
        """Get weather alerts for a location."""
        lat, lon = self.get_location_coords(location)
        
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/onecall", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise click.ClickException(f"Error fetching weather alerts: {str(e)}")

class FavoritesManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.favorites = self._load_favorites()

    def _load_favorites(self) -> List[str]:
        """Load favorites from file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    return json.load(f)
            return []
        except json.JSONDecodeError:
            return []

    def _save_favorites(self):
        """Save favorites to file."""
        with open(self.filename, 'w') as f:
            json.dump(self.favorites, f)

    def add_favorite(self, location: str):
        """Add a location to favorites."""
        if location not in self.favorites:
            self.favorites.append(location)
            self._save_favorites()

    def get_favorites(self) -> List[str]:
        """Get list of favorite locations."""
        return self.favorites

def display_current_weather(weather_data: Dict):
    """Display current weather information in a nice format."""
    weather = weather_data["weather"][0]["description"].capitalize()
    temp = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]

    table = Table(title=f"Current Weather in {weather_data['name']}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Weather", weather)
    table.add_row("Temperature", f"{temp}°C")
    table.add_row("Feels Like", f"{feels_like}°C")
    table.add_row("Humidity", f"{humidity}%")
    table.add_row("Wind Speed", f"{wind_speed} m/s")

    console.print(table)

def display_forecast(forecast_data: Dict):
    """Display weather forecast in a nice format."""
    table = Table(title=f"5-Day Forecast for {forecast_data['city']['name']}")
    table.add_column("Date", style="cyan")
    table.add_column("Weather", style="green")
    table.add_column("Temp (°C)", style="yellow")
    table.add_column("Humidity", style="blue")
    table.add_column("Wind (m/s)", style="magenta")

    for item in forecast_data['list'][::8]:  # Get one forecast per day
        date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
        weather = item['weather'][0]['description'].capitalize()
        temp = f"{item['main']['temp']:.1f}"
        humidity = f"{item['main']['humidity']}%"
        wind = f"{item['wind']['speed']:.1f}"
        
        table.add_row(date, weather, temp, humidity, wind)

    console.print(table)

@click.group()
def cli():
    """Weather CLI - Get weather information for any location."""
    if not API_KEY:
        raise click.ClickException("OpenWeather API key not found. Please set OPENWEATHER_API_KEY in .env file.")
    pass

@cli.command()
@click.argument('location')
def current(location):
    """Get current weather for a location."""
    weather_api = WeatherAPI(API_KEY)
    with Progress() as progress:
        task = progress.add_task("Fetching weather data...", total=1)
        weather_data = weather_api.get_current_weather(location)
        progress.update(task, advance=1)
    display_current_weather(weather_data)

@cli.command()
@click.argument('location')
def forecast(location):
    """Get 5-day forecast for a location."""
    weather_api = WeatherAPI(API_KEY)
    with Progress() as progress:
        task = progress.add_task("Fetching forecast data...", total=1)
        forecast_data = weather_api.get_forecast(location)
        progress.update(task, advance=1)
    display_forecast(forecast_data)

@cli.command()
@click.argument('location')
def alerts(location):
    """Get weather alerts for a location."""
    weather_api = WeatherAPI(API_KEY)
    with Progress() as progress:
        task = progress.add_task("Fetching weather alerts...", total=1)
        alert_data = weather_api.get_alerts(location)
        progress.update(task, advance=1)

    alerts = alert_data.get('alerts', [])
    if not alerts:
        console.print(Panel("No weather alerts for this location", style="green"))
        return

    for alert in alerts:
        console.print(Panel(
            f"[bold red]Alert: {alert['event']}[/]\n\n"
            f"{alert['description']}\n\n"
            f"Start: {datetime.fromtimestamp(alert['start'])}\n"
            f"End: {datetime.fromtimestamp(alert['end'])}",
            title="Weather Alert",
            style="red"
        ))

@cli.command()
@click.argument('location')
def add_favorite(location):
    """Add a location to favorites."""
    weather_api = WeatherAPI(API_KEY)
    # Verify location exists before adding to favorites
    weather_api.get_location_coords(location)
    
    favorites_manager = FavoritesManager(FAVORITES_FILE)
    favorites_manager.add_favorite(location)
    console.print(f"Added [green]{location}[/] to favorites!")

@cli.command()
def favorites():
    """Get weather for all favorite locations."""
    favorites_manager = FavoritesManager(FAVORITES_FILE)
    weather_api = WeatherAPI(API_KEY)
    
    locations = favorites_manager.get_favorites()
    if not locations:
        console.print("No favorite locations saved.")
        return

    with Progress() as progress:
        task = progress.add_task("Fetching weather data...", total=len(locations))
        for location in locations:
            try:
                weather_data = weather_api.get_current_weather(location)
                console.print(f"\nWeather for [bold]{location}[/]:")
                display_current_weather(weather_data)
            except click.ClickException as e:
                console.print(f"Error getting weather for {location}: {str(e)}", style="red")
            progress.update(task, advance=1)

if __name__ == '__main__':
    cli()
