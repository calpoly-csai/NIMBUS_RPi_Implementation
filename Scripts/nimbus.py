'''
Title: NIMBUS Voice Assistant
Author: Chidi Ewenike
Date: 11/15/2019
Organization: Cal Poly CSAI
Description: This is the end-to-end implementation of NIMBUS
             on the Raspberry Pi. GCP Speech-To-Text and
             Text-To-Speech handling was obtained from the
             GCP documentation.

'''

import io
import json
import numpy as np
import os
import pyaudio
import subprocess
import time
import wave

'''
from google.cloud import speech, speech_v1p1beta1
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import texttospeech
'''
from speechpy.feature import mfcc

from Utils.LED import LED
from Utils.WW_Model_Class import Model 
from Utils.OS_Find import Path_OS_Assist

curr_device = "Raspberry Pi 4 - 4 GB"

class NIMBUS_RPi:
    
    def __init__(self):
        
        self.led = LED()

        self.led.recog_flash(0.1, 3, 3)

        # obtain OS-specific delimiter
        self.delim = Path_OS_Assist()
        
        # load the absolute path to the repo
        with open(os.getcwd() + "%sUtils%sPATH.json" % (self.delim, \
            self.delim), "r") as path_json:
            self.REPO_PATH = json.load(path_json)["PATH"]

        # instantiate wake word model class
        self.ww_model = Model()

        # get path for credentials
#        self.credential_path = "auth.json"#"%s%sScripts%sUtils%sData%sauth.json" \
                            #% (self.REPO_PATH, self.delim, 
                            #    self.delim, self.delim, self.delim)
#        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credential_path

        # prediction parameters
        self.CONFIDENCE = 0.6 # prediction confidence 
        self.ACTIVATIONS = 4 # number of activations for confident activation

        # audio input parameters
        self.CHUNK = 2048
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.RECORD_SECONDS = 5

        # mfcc feature parameters
        self.WINDOW = 0.128
        self.STRIDE = 0.064
        self.MFCC = 13
        self.FILTER_BANKS = 20
        self.FFT_NUM = 512

        # pyaudio i/o object instantiation
        self.pa_i = pyaudio.PyAudio()
        self.pa_o = pyaudio.PyAudio()

        # loading speech adaption phrases
        self.Load_Speech_Adaption()

        # instantiate GCP STT & TTS objects
 #       self.stt_client = speech.SpeechClient()
 #       self.tts_client = texttospeech.TextToSpeechClient()

        self.file_name = os.path.join(
                os.path.dirname(__file__),
                'resources',
                'audio.raw')

        # load the desired model
        self.ww_model.load("model.h5")#%s%sScripts%sUtils%sData%smodel.h5" %\
                #(self.REPO_PATH, self.delim, self.delim, self.delim, self.delim))

        # print the summary of the model
        print(self.ww_model.model.summary())

        # open an input audio data stream
        self.istream = self.pa_i.open(format = self.FORMAT, channels = self.CHANNELS, rate = self.RATE, input = True, frames_per_buffer = self.CHUNK)

        # open an output audio data stream
        self.ostream = self.pa_o.open(format = self.FORMAT, channels = self.CHANNELS, rate = 24000, output = True, frames_per_buffer = self.CHUNK)

        # contains the chunks of streamed data
        self.frames = []

        # counts for confident activations
        self.act_count = 0

    def Load_Speech_Adaption(self):
        '''
        Loads phrases needed for understanding uncommon names

        Args: None

        Returns: None

        '''

        # load speech adaption entity names
        with open(os.getcwd() + "%sUtils%sData%sspeech_adaption_entities.txt" % \
                (self.delim, self.delim, self.delim), "r") as spch_ents:
            self.sa_words = [x.replace('\n', '') for x in spch_ents.readlines()]
        
        # concatenated first & last names
        new_name = ""

        # begin concatenating first and last names
        # then adding them to the sa_words
        for i in range(len(self.sa_words)):
            
            if i % 2 == 1:
                new_name += self.sa_words[i]
                self.sa_words.append(new_name)
                new_name = ""
            
            else:
                new_name += (self.sa_words[i] + " ")

        print(self.sa_words)

    def Speech_To_Text(self):
        '''
        Reads the audio input, stores a wave file, then applies speech recognition
        on the audio to produce the corresponding string.

        Args: None

        Returns: result (list of strings) - list of prediction strings

        '''

        # open the input stream
        self.istream.start_stream()

        # stt audio byte array
        stt_frames = []

        # add the audio buffer to the stt audio byte array
        for i in range(0,int(self.RATE/self.CHUNK * self.RECORD_SECONDS)):
            data = self.istream.read(self.CHUNK, exception_on_overflow=False)
            stt_frames.append(data)

        # store the input audio as a wav file
        wf = wave.open("stt.wav", 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.pa_i.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(stt_frames))
        wf.close()
        
        # close the input stream
        self.istream.stop_stream()

        # apply speech adaption
        speech_contexts_element = {"phrases" : self.sa_words}
        speech_contexts = [speech_contexts_element]

        # open the stt wav file
        with io.open("stt.wav", 'rb') as audio_file:
            content = audio_file.read()
            audio = types.RecognitionAudio(content=content)
        
        # configure the STT API
        config = types.RecognitionConfig(
                speech_contexts=speech_contexts, 
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code='en-US')

        # call the STT API and return its response object
        response = self.stt_client.recognize(config, audio)

        # obtain the results from the response object
        result = response.results

        return result

    def Text_To_Speech(self, answer):
        '''
        Takes the input string, runs the TTS API, and outputs the audio

        Args:
                answer (string) - string to be converted to audio

        Returns:
                None
        '''

        # Set the text input to be synthesized
        synthesis_input = texttospeech.types.SynthesisInput(text=answer)

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.types.VoiceSelectionParams(
            language_code='en-US',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

        # Select the type of audio file you want returned
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16)

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = self.tts_client.synthesize_speech(synthesis_input, voice, audio_config)

        # The response's audio_content is binary.
        print(answer)
        self.ostream.write(response.audio_content)

    def Wake_Word(self):
        ''' 
        Runs the wake word and calls the corresponding required functions for the end-to-end response

        Args: None

        Returns: None

        '''

        # reads chunk of audio
        data = self.istream.read(self.CHUNK, exception_on_overflow=False)
       
        self.led.nimbus_refresh()

        # appends chunk to frame list
        self.frames.append(data)

        # begins making predictions after the first 2.5 seconds of audio is read
        if (len(self.frames) > 19):

            # converts first 19 chunks of audio bytes into 16 bit int values
            in_data = np.fromstring(np.array(self.frames[:19]),'Int16')
            
            # extract MFCCs from the 19 chunks of audio
            audio_sig = np.array([mfcc(in_data,self.RATE,self.WINDOW,self.STRIDE,self.MFCC,self.FILTER_BANKS,self.FFT_NUM,0,None,True)])

            # makes predictions
            prediction = self.ww_model.model.predict(audio_sig)

            # if the predictions is larger than the defined confidence
            if (prediction > self.CONFIDENCE):
               
                # increment the activation counter
                self.act_count+=1

                # if the number of consecutive activations exceeds the activation value
                if(self.act_count >= self.ACTIVATIONS):
       
                    # Turn on CSAI Color Scheme
                    self.led.recog_flash(0.001, 1, 2)                 

                    # resets the activation count
                    self.act_count = 0

                    # stops the input stream
                    self.istream.stop_stream()
                    
                    # wake word audio prompt
                    subprocess.Popen(['mpg123', '-q', os.getcwd() + '%sUtils%sData%sNimbus_Awakened.mp3' % (self.delim, self.delim, self.delim)]) 
                    # stalls the program as the audio is played
                    print("\nNIMBUS Activated\n\n")
                    time.sleep(4)
                    
                    # Turn on CSAI Color Scheme
                    # LED.LED_On(CSAI_Colors)      <=============      
                    
                    # obtains the string from the audio input
                    #stt_result = self.Speech_To_Text()
                    
                    #print(stt_result)
                    
                    #answer = ""
                    
                    #best_stt_answer = ""
                    
                    # determines the appropriate input for the NLP engine
                    #if list(stt_result) != []:
                    #    best_stt_answer = stt_result[0].alternatives[0].transcript
              
                    #else:
                    #    answer = "Sorry, I could not hear you. Please ask again."

                    # calls the NLP engine if speech was converted
                    #if best_stt_answer != "":
                    #    answer = "Please ask again later." #NLP(best_stt_answer)
                        
                    # converts the NLP answer to audio
                    #self.Text_To_Speech(answer)

                    self.led.nimbus_refresh()

                    # resets the wake word audio frames
                    self.frames = []

                    # opens the input stream for wake word detection
                    self.istream.start_stream()
            else:
                # print a period for not wake word predictions
                print('.', flush=True, end="")
                
                # reset the activation count
                self.act_count = 0

                # window the data stream
                self.frames = self.frames[1:]

    # TODO
    def Record_Wake_Word(self):
        pass

    # TODO
    def Record_Audio_Data(self):
        # Recording Countdown
        
        # Recording Warning LED 
        # LED.LED_On(YELLOW) <=====
        time.sleep(0.5)
        # LED.LED_Off() <=====
        time.sleep(0.5)

        # LED.LED_On(YELLOW) <=====
        time.sleep(0.5)
        # LED.LED_Off()  <===== 
        time.sleep(0.5)

        # LED.LED_On(YELLOW) <======
        time.sleep(0.5)
        # LED.LED_Off() <========
        time.sleep(0.5)

        # Recording LED Color
        # LED.LED_On(RED)  <========
        # Start Recording

if __name__ == "__main__":       
    nimbus = NIMBUS_RPi()
    # Turn on CSAI Color Scheme
    # LED.LED_On(CSAI_Colors)      <=============              
    
    while True:
       nimbus.Wake_Word() 
