import speech_recognition as sr
import pyttsx3
import torch
import torch.nn as nn
import numpy as np
import json
import random
import webbrowser
import os
from datetime import datetime

# ========== Load AI Model ==========
from model import NeuralNet
from jarvis1 import bag_of_words, tokenize

# Load intents file
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

# ========== Voice Engine ==========
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice

def speak(text):
    """Jarvis speaks out loud."""
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# ========== Speech Recognition ==========
def listen():
    """Listen for voice input and convert to text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Speech recognition service is down.")
        return ""

# ========== Predict Intent ==========
def predict_class(sentence):
    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = torch.from_numpy(X).float()
    output = model(X)
    _, predicted = torch.max(output, dim=0)
    tag = tags[predicted.item()]
    return tag

# ========== Perform Action ==========
def perform_task(tag):
    if tag == "time":
        now = datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {now}")

    elif tag == "open_browser":
        speak("which Browser do you want to open?")
        browser = listen()
        if "chrome" in browser:
            webbrowser.open("https://www.google.com/chrome/")
        elif "firefox" in browser:
            webbrowser.open("https://www.mozilla.org/firefox/")
        else:
            speak("Sorry, I can only open Chrome or Firefox.")
        speak("Opening browser...")
        webbrowser.open("https://www.google.com")

    elif tag == "shutdown":
        speak("Shutting down your system. Goodbye!")
        os.system("shutdown /s /t 1")

    elif tag == "tell_me_a_joke":
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the computer go to therapy? It had too many bytes of anxiety!",
            "I'm reading a book about anti-gravity. It's impossible to put down!"
        ]
        speak(random.choice(jokes))

    elif tag == "greet":
        speak("Hello! How can I help you today?")

    elif tag == "exit":
        speak("Goodbye! Have a nice day.")
        exit()

    else:
        speak("Sorry, I don't know how to do that yet.")

# ========== Main Loop ==========
def jarvis():
    speak("Hello Rudraksh! Jarvis is now online.")
    while True:
        command = listen()
        if command:
            tag = predict_class(command)
            print(f"Predicted intent: {tag}")
            perform_task(tag)

# Run Jarvis
jarvis()
