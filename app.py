import speech_recognition as sr
from dotenv import load_dotenv
import pyttsx3
import pywhatkit
import datetime
import pyjokes
import requests
from groq import Groq
import os

load_dotenv('.env')

api_key = os.getenv('GROQ_API_KEY')
weather_api_key = os.getenv('WEATHER_API_KEY')

client = Groq(api_key=api_key)

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # You can change the voice index if you prefer another voice

def talk(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def get_groq_response(prompt):
    """Get a response from Groq's language model."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gemma2-9b-it",  # Replace with your chosen model
            stream=False,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred while communicating with Groq: {e}"

def get_weather(city):
    """Fetch weather information for a specified city using OpenWeatherMap API."""
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric'
        response = requests.get(url)
        data = response.json()
        if data["cod"] != "404":
            weather = data["main"]
            temperature = weather["temp"]
            humidity = weather["humidity"]
            description = data["weather"][0]["description"]
            weather_report = f"The temperature in {city} is {temperature}°C with {description} and humidity of {humidity}%."
        else:
            weather_report = "City not found."
    except Exception as e:
        weather_report = f"Error occurred: {e}"
    return weather_report

def take_command():
    """Listen for a voice command and return the recognized text."""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'assistant' in command:
                command = command.replace('assistant', '')
                print(f'You said: {command}')
    except Exception as e:
        print(e)
        command = ""
    return command

def run_assistant():
    """Run the assistant to execute commands based on voice input."""
    command = take_command()
    if command:
        if 'play' in command:
            song = command.replace('play', '')
            talk('Playing ' + song)
            pywhatkit.playonyt(song)
        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            talk('Current time is ' + time)
        elif 'joke' in command:
            talk(pyjokes.get_joke())
        elif 'weather' in command:
            city = command.replace('weather', '').strip()
            if city:
                weather_report = get_weather(city)
                talk(weather_report)
            else:
                talk("Please specify a city to get the weather report.")
        else:
            response = get_groq_response(command)
            talk(response)

while True:
    run_assistant()
