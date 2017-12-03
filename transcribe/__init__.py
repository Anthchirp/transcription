# Bing subscriptions: https://www.microsoft.com/cognitive-services/en-us/subscriptions
# Du brauchst "Bing speech"
#
# DO NOT RUN ON CLOUD DRIVE
#

from os import path
import speech_recognition as sr
import time
import wave

def main():
  filename = path.join(path.dirname(path.realpath(__file__)), "output.wav")
  language = "de-DE"

  if language == 'en-US':
    with open("output_sphinx.txt", "a") as fh:
      fh.write("\n\nSphinx text recognition\n")
  with open("output_bing.txt", "a") as fh:
    fh.write("\n\nBing text recognition\n")

  w = wave.open(filename, 'r')
  start_frame = 0
  length = w.getnframes()
  block_size = w.getframerate() * 11 # Sekunden
  overlap = w.getframerate()    *  1 # Sekunden

  lastframeend = start_frame
  rate_limit = 0
  while lastframeend < w.getnframes()-1:
    start = max(0, lastframeend - overlap)
    end = min(lastframeend + block_size, w.getnframes()-1)
    lastframeend = end + 1
    print (str(start) + ' to ' + str(end))
    w.setpos(start) # Set position on the original wav file
    chunkData = w.readframes(end-start) # And read to where we need
   
    chunkAudio = wave.open("temp.wav",'w')
    chunkAudio.setnchannels(w.getnchannels())
    chunkAudio.setsampwidth(w.getsampwidth())
    chunkAudio.setframerate(w.getframerate())
    chunkAudio.writeframes(chunkData)
    chunkAudio.close()

    timecode = int(start / w.getframerate())
    timecode = "[%02d:%02d] " % (int(timecode / 60), timecode % 60)

    print(timecode)

    # use the audio file as the audio source
    r = sr.Recognizer()
    print("Loading...")
    with sr.AudioFile("temp.wav") as source:
      audio = r.record(source) # read the entire audio file
    print("Recognizing...")
  
    # recognize speech using Sphinx
    if language == 'en-US':
      try:
        recognized = r.recognize_sphinx(audio, language=language)
        with open("output_sphinx.txt", "a") as fh:     
          fh.write("\n" + timecode)
          fh.write(recognized.encode("UTF-8") + "\n")
        print("Sphinx thinks you said:")
        print(recognized)
      except sr.UnknownValueError:
        print("Sphinx could not understand audio")
      except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))
  
  # recognize speech using Google Speech Recognition
  #try:
  #    # for testing purposes, we're just using the default API key
  #    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
  #    # instead of `r.recognize_google(audio)`
  #    print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
  #except sr.UnknownValueError:
  #    print("Google Speech Recognition could not understand audio")
  #except sr.RequestError as e:
  #    print("Could not request results from Google Speech Recognition service; {0}".format(e))
  
  # recognize speech using Wit.ai
  #WIT_AI_KEY = "INSERT WIT.AI API KEY HERE" # Wit.ai keys are 32-character uppercase alphanumeric strings
  #try:
  #    print("Wit.ai thinks you said " + r.recognize_wit(audio, key=WIT_AI_KEY))
  #except sr.UnknownValueError:
  #    print("Wit.ai could not understand audio")
  #except sr.RequestError as e:
  #    print("Could not request results from Wit.ai service; {0}".format(e))
  
  # recognize speech using Microsoft Bing Voice Recognition
    BING_KEY = "asdf"
    try:
      if time.time() < rate_limit + 3.1:
        print ("Waiting...")
        time.sleep(3.1 + rate_limit - time.time())
        print ("Go.")
      rate_limit = time.time()
      recognized = r.recognize_bing(audio, language=language, key=BING_KEY, show_all=True)
      with open("output_bing.txt", "a") as fh:
          for entry in recognized.get('results', []):
  #        fh.write("\n" + timecode + "parsed: " + entry.get('name').encode("UTF-8") + "\n")
              fh.write(timecode + entry.get('lexical').encode("UTF-8") + "\n")
  #        fh.write("test" + results + "\n")
          print("Microsoft Bing Voice Recognition:")
          try:
            print(entry.get('name'))
          except:
            pass
    except sr.UnknownValueError:
      print("Microsoft Bing Voice Recognition could not understand audio")
    except sr.RequestError as e:
      print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))
  
  # recognize speech using Houndify
  #HOUNDIFY_CLIENT_ID = "INSERT HOUNDIFY CLIENT ID HERE" # Houndify client IDs are Base64-encoded strings
  #HOUNDIFY_CLIENT_KEY = "INSERT HOUNDIFY CLIENT KEY HERE" # Houndify client keys are Base64-encoded strings
  #try:
  #    print("Houndify thinks you said " + r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY))
  #except sr.UnknownValueError:
  #    print("Houndify could not understand audio")
  #except sr.RequestError as e:
  #    print("Could not request results from Houndify service; {0}".format(e))
  
  # recognize speech using IBM Speech to Text
  #IBM_USERNAME = "INSERT IBM SPEECH TO TEXT USERNAME HERE" # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
  #IBM_PASSWORD = "INSERT IBM SPEECH TO TEXT PASSWORD HERE" # IBM Speech to Text passwords are mixed-case alphanumeric strings
  #try:
  #    print("IBM Speech to Text thinks you said " + r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD))
  #except sr.UnknownValueError:
  #    print("IBM Speech to Text could not understand audio")
  #except sr.RequestError as e:
  #    print("Could not request results from IBM Speech to Text service; {0}".format(e))

