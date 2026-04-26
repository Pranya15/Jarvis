import speech_recognition as sr  
import webbrowser
import pyttsx3
import time
import musiclibrary
import requests
import os
import pygame
from openai import OpenAI
from gtts import gTTS

# Debug: Check if API key is loaded
print("KEY:", os.getenv("OPENAI_API_KEY"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = "pub_536ff07a635d413bae3da4c288859ee1"

# Simple memory dictionary 
memory = {}

recognizer = sr.Recognizer()
engine = pyttsx3.init('sapi5')

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Old offline voice (kept for backup)
def speak_old(text):
    print("Jarvis:", text)   
    engine.stop()
    engine.say(text)
    engine.runAndWait()

# Main speak function using gTTS (online voice)
def speak(text):
    tts = gTTS(text)
    tts.save("temp.mp3")

    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.music.unload()  

    time.sleep(0.5) 
    os.remove("temp.mp3")

# AI processing function
def aiProcess(command):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are Jarvis. Give short helpful answers."},
                {"role": "user", "content": command}   
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("AI Error:", e)

        # Handle quota error gracefully
        if "quota" in str(e):
            return "I am out of credits. Please enable billing."
        return "Sorry, I am unable to connect right now."

# News function
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

# Main command processor
def processCommand(c):
    c = c.lower()

    # Open fixed websites
    if "open google" in c:
        webbrowser.open("https://google.com")

    elif "open instagram" in c:
        webbrowser.open("https://instagram.com")

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")

    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")

    # Open ANY website dynamically
    elif c.startswith("open"):
        site = c.replace("open", "").strip()
        webbrowser.open(f"https://{site}.com")
        speak(f"Opening {site}")

    # News
    elif "news" in c:
        get_news()

    # Time feature
    elif "time" in c:
        current_time = time.strftime("%H:%M")
        speak(f"The time is {current_time}")

    # Date feature
    elif "date" in c:
        current_date = time.strftime("%d %B %Y")
        speak(f"Today is {current_date}")

    # Memory feature
    elif "my name is" in c:
        name = c.replace("my name is", "").strip()
        memory["name"] = name
        speak(f"Got it, {name}")

    elif "what is my name" in c:
        speak(memory.get("name", "I don't know your name yet"))

    # Music play
    elif c.startswith("play"):
        song = c.replace("play", "").strip().replace(" ", "")

        if song in musiclibrary.music:
            webbrowser.open(musiclibrary.music[song])
        else:
            # NEW: Play from YouTube if not found
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
            speak("Playing from YouTube")

    # AI fallback
    else:
        output = aiProcess(c)
        print("AI Response:", output)  # debug
        speak(output)

# Main program
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

            # Wake word logic
            if "jarvis" in word.lower():
                speak("Yes")

                command = word.lower().replace("jarvis", "").strip()

                # If command already in same sentence
                if command:
                    processCommand(command)
                else:
                    # Listen again for command
                    with sr.Microphone() as source:
                        print("Waiting for command...")
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        command = recognizer.recognize_google(audio)
                        processCommand(command)

        except Exception as e:
            print("Error:", e)
