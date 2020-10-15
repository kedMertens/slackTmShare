import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from onboarding_tutorial import OnboardingTutorial
from telegram import Bot
import requests
import hubWrapper
import subprocess

#init your api

slackApiKey = ''
token = ''
telegramBotToken = ''
telegramChatId = ''

app = Flask(__name__)

slack_events_adapter = SlackEventAdapter(slackApiKey, "/slack/events", app)
slack_web_client = WebClient(token=token)

channelID = ''

tm = Bot(telegramBotToken)
rxFile = ''
fileRecieved = False

def setFileRXStatus(status):
    global fileRecieved 
    fileRecieved = status
def getFileRXStatus():
    global fileRecieved
    return fileRecieved

def getFile(url,fileName):
    response = requests.get(url, headers={'Authorization': 'Bearer %s' % token})
    file = open("storage/" + fileName, "wb+")
    file.write(response.content)
    file.close()


def sendFile(channelID, file, title):
    slack_web_client.files_upload(channels= channelID, file=file, title=title)

@slack_events_adapter.on("message")
def message(payload):
    global rxFile
    event = payload.get("event", {})

    channel_id = event.get("channel")
    global channelID
    channelID = channel_id
    user_id = event.get("user")
    text = event.get("text")
    files = event.get("files")
    print(event)
    print("message RX" + ' ' + text)
    print("channelID " + channelID)

    payload = {
                "channel": channel_id,
                "username": user_id,
                "blocks": [
                {
                    "type": "section",
                    "text": {
                                "type": "plain_text",
                                "text": "Do you want to push the file?",
                            }
                },
               ]
            }

    if files and not files[0]['title'] == "shared from Telegram" and not files[0]['title'] == "got from textile":
        print(files)
        rxFile =  files[0]
        setFileRXStatus(True)
        slack_web_client.chat_postMessage(**payload)
    elif text and (text == 'yes' or text == 'no') and getFileRXStatus():
        if text == 'yes':
            textToSend = "Pushing..."
        else:
            textToSend = "Not pushing"
        slack_web_client.chat_postMessage(channel = channel_id, text = textToSend)
        setFileRXStatus(False)
        
        if textToSend == "Pushing...":
            print(rxFile)
            getFile(rxFile['url_private_download'], rxFile['name'])
            fileToShare = open(pathToTextileBucket + rxFile['name'],'rb')
            tm.sendDocument(chat_id = telegramChatId, document = fileToShare)
            hubWrapper.hubBucketPush()
    if text and text == 'get':
            slack_web_client.chat_postMessage(channel = channel_id, text = "Pulling...")
            hubWrapper.callHub('pull')
            res = subprocess.run(['ls'], capture_output=True, cwd = pathToTextileBucket)
            slack_web_client.chat_postMessage(channel = channel_id, text = res.stdout.decode('utf-8'))
    if text and text[:3] == 'get' and text[3:]:
            slack_web_client.chat_postMessage(channel = channel_id, text = "Preparing to share the file...")
            sendFile(channel_id, pathToTextileBucket + text[4:], 'got from textile')
        

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)
