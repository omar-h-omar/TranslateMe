"""
IMPORTANT: please run this command first to export your google client keys to the os.
export GOOGLE_APPLICATION_CREDENTIALS="./googlekey.json"
"""
GOOGLE_APPLICATION_CREDENTIALS = "./googlekey.json"
from twilio.rest import Client
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
account_sid = "YOUR ACCOUNT SID"
auth_token  = "YOUR ACCOUNT AUTH TOKEN"
client = Client(account_sid, auth_token)
from flask import Flask, request, redirect
import requests
from twilio.twiml.messaging_response import MessagingResponse
from flask import send_file
import io
import os
import mimetypes
from urllib.parse import urlparse



translate_client = translate.Client()
def translate(body):
    """
    Translates the text message into the desired language and
        calls upon the voice function to generate a pronunciation of such text.
    Args:
    body: a string containing the text to be translated with the last word
        being the target language to translate the text into.
    Returns:
    body: if no target language is found returns the original message
    translation: if a target language is found returns a string with the correct translation. 
    """
    text = body
    lang_list = translate_client.get_languages()
    words = body.split()
    target_lang =''
    length = len(words) -1
    lastword = words[length]
    for lang in lang_list:
        if lastword.lower() == lang['name'].lower():
            target_lang = lang['language']
    if lastword.lower() == "chinese":
        target_lang = 'zh'
    if target_lang == "":
        voice(text,target_lang='en')
        return body
    out = ''
    body = body.split()
    for word in body[0:len(body) -1]:
        out += word
        out += ' '
    output = translate_client.translate(
    out, target_language=target_lang)
    translation = output['translatedText']
    voice(translation,target_lang)
    return translation

client = texttospeech.TextToSpeechClient() #Initialises the text to speech client from google
def voice(text1,target_lang):
    """
    Generates an audio file containing the pronunciation of text.
    Args:
    text1: A string containing the text to be converted to audio.
    target_lang: A string of the desired language to translate the text into. 
        Note: this string has to be in the shortened format for example: English would be en.
    Returns:
    output.mp3: an audio file containg the pronunciation of text1.
    """
    lang_dict = {'ar':'ar-XA','en':'en-GB','cs':'cs-CZ','da':'da-DK','nl':'nl-NL','fi':'fi-FI','fr':'fr-FR','de':'de-DE','el':'el-GR','hi':'hi-IN','hu':'hu-HU','id':'id-ID','it':'it-IT','ja':'ja-JP','ko':'ko-KR','zh':'cmn-CN','no':'nb-NO','pl':'pl-PL','pt':'pt-BR','ru':'ru-RU','sk':'sk-SK','es':'es-ES','sv':'sv-SE','tr':'tr-TR','uk':'uk-UA','vi':'vi-VN'}
    # A dictionary of all languages supported.
    lang_code = ''
    for key,val in lang_dict.items():
        if target_lang == key:
            lang_code = val
    if lang_code == '':
        lang_code = 'en-GB'
    synthesis_input = texttospeech.types.SynthesisInput(text=text1)
    voice = texttospeech.types.VoiceSelectionParams(
    language_code=lang_code,
    ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.types.AudioConfig(
    audio_encoding=texttospeech.enums.AudioEncoding.MP3)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    with open('output.mp3', 'wb') as out: #Writes an audio file with the name output.mp3
        out.write(response.audio_content)

app = Flask(__name__)
@app.route('/audio1')#Creates a new path of /audio in local host to allow for http requests.
def get_audio():
    """
    Returns a messaging response to the Twillo client the audio file output.mp3 containg the pronunciation and 
        deletes that file from the directory.
    """
    filename = "output.mp3"
    response = send_file(filename, mimetype='audio/mpeg')
    response.headers['Cache-Control'] = 'no-cache'
    os.remove(filename)
    return response
@app.route("/sms", methods=['GET', 'POST'])#Creates a new path of /sms in local host to allow for http requests.
def incoming_sms():
    """
    Returns a message response to the Twillo client with the translated text and
        creates a request to /audio in the local host.
    Returns:
    response: if the message to be translated was hello or bye returns a custom message
        Otherwise a message with the translated text.
    """
    lang_dict = {'ar':'ar-XA','en':'en-GB','cs':'cs-CZ','da':'da-DK','nl':'nl-NL','fi':'fi-FI','fr':'fr-FR','de':'de-DE','el':'el-GR','hi':'hi-IN','hu':'hu-HU','id':'id-ID','it':'it-IT','ja':'ja-JP','ko':'ko-KR','zh':'cmn-CN','no':'nb-NO','pl':'pl-PL','pt':'pt-BR','ru':'ru-RU','sk':'sk-SK','es':'es-ES','sv':'sv-SE','tr':'tr-TR','uk':'uk-UA','vi':'vi-VN'}
    body = request.values.get('Body', None)
    resp = MessagingResponse()
    if body == 'hello':
        resp.message("Hi! I am your helper bot and I can help you translate stuff. Just send what you need to be translated. :)")
    elif body == 'bye':
        resp.message("Goodbye. Hope you enjoyed our test program")
    elif body != '':
        translation = translate(body)
        resp.message(translation)
        lang_list = translate_client.get_languages()
        words = body.split()
        length = len(words) -1
        lastword = words[length]
        target_lang = ''
        for lang in lang_list:
            if lastword.lower() == lang['name'].lower():
                target_lang = lang['language']
        if target_lang in lang_dict.keys():
            response = MessagingResponse()
            msg = resp.message("")
            msg.media("https://e0c5fe4c.ngrok.io/audio1")
    else:
        num_media = int(request.values.get("NumMedia"))
        media_files = []
        for idx in range(num_media):
            media_url = request.values.get("MediaUrl{}".format(idx))
            mime_type = request.values.get("MediaContentType{}".format(idx))
            media_files.append((media_url, mime_type))
            req = requests.get(media_url)
            file_extension = mimetypes.guess_extension(mime_type)
            media_sid = os.path.basename(urlparse(media_url).path)
            with open("{}{}".format(media_sid,file_extension), 'wb') as f:
                f.write(req.content)
        client = speech.SpeechClient()
        file_name = media_sid+file_extension
        with io.open(file_name, 'rb') as audio_file:
            content = audio_file.read()
            audio = types.RecognitionAudio(content=content)
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code='en-GB')
        response = client.recognize(config, audio)
        sentence = 'test'
        for result in response.results:
            sentence += '{}'.format(result.alternatives[0].transcript)
        resp.message(sentence)
        os.remove(file_name)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
