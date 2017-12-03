# Best not to run this in a directory where other software tries to sync stuff
# (dropbox, google drive, onedrive, etc.)

from __future__ import absolute_import, division, print_function

from optparse import SUPPRESS_HELP, OptionParser
import os
import string
import sys
import time
import wave

import speech_recognition as sr

def transcribe(filename, basename, mechs=None, seconds=11):
  if not mechs:
    print("No transcription mechanisms specified, skipping")
    return
  if not os.path.exists(filename):
    print("Audio input file does not exist, skipping")
    return

  w = None
  try:
    w = wave.open(filename, 'r')
    start_frame = 0
    length = w.getnframes()
    block_size = w.getframerate() * seconds # 11 seconds (default) recognition snippets
    overlap = w.getframerate()    *  1      #  1 second overlap between blocks
    lastframeend = start_frame

    for m in mechs:
      m.start(basename)

    while lastframeend < w.getnframes()-1:
      start = max(0, lastframeend - overlap)
      end = min(lastframeend + block_size, w.getnframes()-1)
      lastframeend = end + 1
      print("Processing {start} to {end}".format(start=start, end=end))
      w.setpos(start) # Set position on the original wav file
      chunkData = w.readframes(end-start) # And read to where we need

      # Create temporary file containing snippet of audio for processing  
      chunkAudio = None
      tempfile = 'temp.wav'
      try: 
        chunkAudio = wave.open(tempfile,'w')
        chunkAudio.setnchannels(w.getnchannels())
        chunkAudio.setsampwidth(w.getsampwidth())
        chunkAudio.setframerate(w.getframerate())
        chunkAudio.writeframes(chunkData)
      finally:
        if chunkAudio:
          chunkAudio.close()

      timecode = int(start / w.getframerate())
      timecode = "[%02d:%02d] " % (int(timecode / 60), timecode % 60)

      for m in mechs:
        m.recognize(tempfile, timecode)
  finally:
    if w:
      w.close()
    for m in mechs:
      m.done()
  print("All done.")

def main():
  parser = OptionParser(usage="transcribe [options] file [file ..]",
                        description="Transcribe one or more files to text using different methods.")
  parser.add_option("-?", action="help", help=SUPPRESS_HELP)
  parser.add_option("-b", "--bing", dest="bing", metavar="APIKEY",
      action="store", type="string", default=None,
      help="Bing API key. Register at https://www.microsoft.com/cognitive-services/en-us/subscriptions for 'Bing speech'.")
  parser.add_option("-l", "--language", dest="language", metavar="LANG",
      action="store", type="choice", default='en-US', choices=['en-US', 'de-DE'],
      help="Language of audio file (supported: en-US=english (default), de-DE=german)")
  parser.add_option("-s", "--snip", dest="blocksize",
      action="store", type="int", default=11,
      help="Snippet length in seconds for transcription (default: 11. Bing limit: <15)")
  options, args = parser.parse_args()

  if not args:
    parser.print_help()
    sys.exit(0)

  mechs = []

  if options.bing:
    mechs.append(transcribe_bing(options))
  elif options.language == 'en-US':
    # Only run Sphinx if bing is not selected
    mechs.append(transcribe_sphinx(options))
  elif options.language == 'de-DE':
    # Sphinx can only do en-US
    pass

  try:
    for f in args:
      print("Transcribing file {filename} with language {language} using mechs {mechs}".format(filename=f, language=options.language, mechs=", ".join(map(repr, mechs))))
      basename = os.path.splitext(f)[0]
      transcribe(f, basename, mechs=mechs, seconds=options.blocksize)
  except KeyboardInterrupt:
    print("\nStopped by user.")

class transcribe_sphinx():
  def __repr__(self):
    return "Sphinx"

  def __init__(self, options):
    self.recognizer = sr.Recognizer()
    self.language = options.language
    self.output_file = None

  def start(self, basename):
    self.done()
    outname = basename + '_sphinx.txt'
    self.output_file = open(outname, 'w')
    print("Writing sphinx transcription to {0}".format(outname))

  def recognize(self, tempfile, timecode):
    with sr.AudioFile(tempfile) as source:
      audio = self.recognizer.record(source) # read the snippet file
    # recognize speech using Sphinx
    try:
      recognized = self.recognizer.recognize_sphinx(audio, language=self.language)
      self.output_file.write(timecode)
      self.output_file.write(recognized.encode("UTF-8", 'replace') + "\n")
      if recognized:
        try:
          print("Sphinx thinks you said:", recognized)
        except UnicodeEncodeError:
          print("Sphinx found results with a special character (see output file)")
    except sr.UnknownValueError:
      print("Sphinx could not understand audio")
    except sr.RequestError as e:
      print("Sphinx error: {0}".format(e))

  def done(self):
    if self.output_file:
      self.output_file.close()
      self.output_file = None

class transcribe_bing():
  def __repr__(self):
    return "Microsoft Bing"

  def __init__(self, options):
    self.recognizer = sr.Recognizer()
    self.language = options.language
    self.api_key = options.bing
    self.output_file = None
    self.raw_file = None
    self.debug_file = None
    self.last_request = 0
    self.rate_limit = 3.1 # minimum number of seconds between requests

  def start(self, basename):
    self.done()
    outname = basename + '_bing.txt'
    rawname = basename + '_bing_raw.txt'
    debname = basename + '_bing_debug.txt'
    self.output_file = open(outname, 'w')
    self.raw_file = open(rawname, 'w')
    self.debug_file = open(debname, 'w')
    print("Writing bing transcription to {}".format(outname))
    print("Writing bing transcription without punctuation to {}".format(rawname))
    print("Writing bing debug information to {}".format(debname))

  def recognize(self, tempfile, timecode):
    with sr.AudioFile(tempfile) as source:
      audio = self.recognizer.record(source) # read the snippet file
    # recognize speech using Bing
    wait_time = self.last_request + self.rate_limit - time.time()
    if wait_time > 0:
      time.sleep(wait_time)
    self.last_request = time.time()
    try:
      recognized = self.recognizer.recognize_bing(audio, language=self.language, key=self.api_key, show_all=True)
      self.debug_file.write("%s %s\n" % (timecode, recognized))
      if recognized.get('RecognitionStatus') == 'Success':
        self.output_file.write(timecode + recognized.get('DisplayText').encode("UTF-8", 'xmlcharrefreplace') + "\n")
        self.raw_file.write(timecode + recognized.get('DisplayText').encode("UTF-8", 'ignore').translate(None, string.punctuation) + "\n")
        try:
          print("Bing thinks you said: %s" % recognized.get('DisplayText'))
        except UnicodeEncodeError:
          try:
            print("Bing thinks you said: %s" % recognized.get('DisplayText').encode('ascii', 'replace'))
          except UnicodeEncodeError:
            print("Bing found results with a special character (see output file)")
      else:
        print("Bing did not recognize this")
    except sr.UnknownValueError:
      print("Microsoft Bing Voice Recognition could not understand audio")
    except sr.RequestError as e:
      print("Could not request results from Microsoft Bing Voice Recognition service: {0}".format(e))
      error_line = "%s RequestError: %s\n" % (timecode, e.reason)
      self.debug_file.write(error_line)
      self.output_file.write(error_line)
      self.raw_file.write(error_line)

  def done(self):
    if self.output_file:
      self.output_file.close()
      self.output_file = None
    if self.raw_file:
      self.raw_file.close()
      self.raw_file = None
    if self.debug_file:
      self.debug_file.close()
      self.debug_file = None
