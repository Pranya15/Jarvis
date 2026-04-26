import speech_recognition as sr  
import webbrowser
import pyttsx3
import time
import musiclibrary
import requests
import os
import pygame
from openai import OpenAI
from gtts import gTTs

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = "pub_536ff07a635d413bae3da4c288859ee1"

recognizer = sr.Recognizer()
engine = pyttsx3.init('sapi5')

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak_old(text):
    print("Jarvis:", text)   
    engine.stop()
    engine.say(text)
    engine.runAndWait()

def speak(text):
    tts = gTTs(text)
    tts.save("temp.mp3")

    # Initialize pygame mixer
    pygame.mixer.init()

    # Load the MP3 file
    pygame.mixer.music.load()

    # Play the MP3 file
    pygame.mixer.music.play()

    # Keep the program running until the music stops playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    os.remove("temp.mp3")


def aiProcess(command):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant named Jarvis  skilled in general tasks like alexa and google cloud. Give short responses"},
                {"role": "user", "content": command}   
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("AI Error:", e)
        return "Sorry, I am unable to connect right now."

def get_news():
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&country=in&language=en"

    try:
        response = requests.get(url)
        data = response.json()

        articles = data.get("results", [])[:3]

        if not articles:
            speak("No news found")
            return

        speak("Here are the top news updates")

        for article in articles:
            title = article.get("title", "")
            speak(title)
            time.sleep(0.5)

    except Exception as e:
        print("News Error:", e)
        speak("Unable to fetch news")

def processCommand(c):
    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")

    elif "open instagram" in c:
        webbrowser.open("https://instagram.com")

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")

    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")

    elif "news" in c:
        get_news()

    elif c.startswith("play"):
        song = c.replace("play", "").strip().replace(" ", "")

        if song in musiclibrary.music:
            webbrowser.open(musiclibrary.music[song])
        else:
            speak("Song not found")

    else:
        output = aiProcess(c)
        speak(output)

if __name__ == "__main__":
    speak("Initializing Jarvis")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            word = recognizer.recognize_google(audio)
            print("Heard:", word)

            if "jarvis" in word.lower():
                speak("Yes")

                command = word.lower().replace("jarvis", "").strip()

                if command:
                    processCommand(command)
                else:
                    with sr.Microphone() as source:
                        print("Waiting for command...")
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        command = recognizer.recognize_google(audio)
                        processCommand(command)

        except Exception as e:
            print("Error:", e)