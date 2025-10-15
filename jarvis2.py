import speech_recognition as sr
import pyttsx3
import torch
import json
import random
import webbrowser
import os
from datetime import datetime
from model import NeuralNet
from jarvis1 import tokenize, bag_of_words
import subprocess
import pyautogui
import webbrowser
import os
from datetime import datetime

# Load intents
with open(r"C:\Users\rudra\OneDrive\Documents\python\jarvis\intents.json", "r") as f:
    intents = json.load(f)

# Load trained model
FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size)
model.load_state_dict(model_state)
model.eval()

# Initialize TTS
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def predict_class(sentence):
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = torch.from_numpy(X).float()
    output = model(X)
    _, predicted = torch.max(output, dim=0)
    return tags[predicted.item()]

def execute_command(tag):
    """Perform actions based on recognized tag."""
    
    # TIME
    if tag == "time":
        now = datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}"

    # OPEN BROWSER
    elif tag == "open_browser":
        webbrowser.open("https://www.google.com")
        return "Opening browser."

    # PLAY MUSIC (Windows default player)
    elif tag == "play_music":
        music_path = r"C:\Users\rudra\Music"  # Change this path to your music folder
        os.startfile(music_path)
        return "Playing music now."

    # PAUSE MUSIC - Windows Media Keys
    elif tag == "pause_music":
        pyautogui.press("playpause")
        return "Music paused."

    # VOLUME UP
    elif tag == "volume_up":
        pyautogui.press("volumeup")
        return "Increasing volume."

    # VOLUME DOWN
    elif tag == "volume_down":
        pyautogui.press("volumedown")
        return "Decreasing volume."

    # MUTE
    elif tag == "mute":
        pyautogui.press("volumemute")
        return "Muting volume."

    # OPEN NOTEPAD
    elif tag == "open_notepad":
        subprocess.Popen(["notepad.exe"])
        return "Opening Notepad."

    # OPEN CALCULATOR
    elif tag == "open_calculator":
        subprocess.Popen(["calc.exe"])
        return "Opening Calculator."

    # SHUTDOWN
    elif tag == "shutdown":
        os.system("shutdown /s /t 1")
        return "Shutting down your system."

    # RESTART
    elif tag == "restart":
        os.system("shutdown /r /t 1")
        return "Restarting your system."

    # JOKE
    elif tag == "joke":
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the computer go to therapy? It had too many bytes of anxiety!",
            "I'm reading a book on anti-gravity. It's impossible to put down!"
        ]
        return random.choice(jokes)

    # GREETINGS
    elif tag == "greet":
        return "Hello! How can I assist you today?"

    # EXIT
    elif tag == "exit":
        return "Goodbye! See you soon."

    else:
        return "I'm not sure how to handle that yet."

def process_text_command(command):
    """Takes text input and returns AI response."""
    tag = predict_class(command)
    response = execute_command(tag)
    speak(response)
    return response

def listen_for_command():
    """Listens for a voice command and processes it."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print(f"You said: {command}")
        return process_text_command(command.lower())
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError:
        return "Speech recognition service is down."
# Jarvis backend function
def jarvis_backend(command):
    """This will be imported by the frontend."""
    return process_text_command(command)


if __name__ == "__main__":
    # If you run this file directly, it will start voice recognition
    while True:
        response = listen_for_command()
        if response == "Goodbye!":
            break
