# TranslateMe
Translate Text over SMS and Get its Pronunciation

Note: This is my first GitHub repository so I apologize in advance for any messy code or unexplained sections of code. Please email me at omarhatem5555@gmail.com for any queries.

A Flask App that allows you to translate text over SMS or WhatsApp. This App uses both the Twillo API and the Google API to allow for rapid SMS (Twillo) and quick Translation (Google Translate)

# How to use?
Send any message you want to translate with the language you want to translate that message to at the end of your message 
Example: Hello World German would translate to Hallo Welt.

Please note that if the sentence contains the name of the language like I am German you still need to add the target language, for instance, German at the end again to be I am German German.

The Translation received will not contain the name of the language at the end.

Also, depending on the language TranslateMe would reply with both the translation and the audio file with the pronunciation of the translated text. The list of all supported languages for pronunciation can be found at https://cloud.google.com/text-to-speech/docs/voices .

# Requirements:
1. A Twilio account with balance for the SMS/WhatsApp messages to be sent.
2. A Google developer account for the translation.
3. An environment with both the Twilio and Google APIs installed.
4. Ngrok to use for HTTP request

# Steps:
Firstly you will need to sign up for a Twilio account. You can get a free trial account with $15 of balance when you sign up at http://twilio.com . After you have an account please either sign up for a number to use for SMS or use the WhatsApp sandbox to use for WhatsApp messages. Lastly, don't forget to copy the ACCOUNT SID and AUTH TOKEN into the code where requested.

The next step would be to sign up for a Google developer account https://console.developers.google.com . You will need to enable the google translate API and get your google credentials JSON file into the project directory. More info on credentials available at https://cloud.google.com/docs/authentication/getting-started .

Now that you're all set up you will need to make a python virtual environment and install both the google and Twillo APIs using pip. More information can be found at https://www.twilio.com/docs/libraries/python and https://developers.google.com/docs/api/quickstart/python .

Once you have done that sign up for a Ngrok account and follow their setup process to enable HTTP requests from the internet on your local machine. Note: Better implementations may exist out there. This is only what I used.

Finally, update your Twilio webhooks to the link provided by Ngrok with /sms at the end. Now you can run the code and you should have a working translator.

# How it works?
Under the hood, when you send a message to the number provided by Twilio. A request is made using the webhooks to your local machine using the link provided by Ngrok with /sms added at the end. This GET request contains the body of the message you sent which is then split up to identify the target language of translation.

A request is then made to the Google Servers asking for the translation and pronunciation of the aforementioned translation. Lastly, both the translation and pronunciation are sent back and the audio file for the pronunciation is deleted from your directory.
