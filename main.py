from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from apiclient import errors 
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

SCOPES = ['https://mail.google.com/']

def getMyProfile(service):
    try:
        profile = service.users().getProfile(userId = 'me').execute()
        for labels in profile:
            return(labels, " : ", profile[labels])

    except errors.HttpError as error:
        print(f"An error occured: {error}")

def getDictMessage(service):
    try:
        search_id = service.users().messages().list(userId='me').execute()
        return search_id
    
    except errors.HttpError as error:
        print(f"An error occured: {error}")

def getListOfMessageID(service):
    try:
        dictOfMessages = getDictMessage(service)
        list_of_messageID = [] 
        for everyList in dictOfMessages['messages']:
            list_of_messageID.append(everyList['id'])
        return list_of_messageID

    except errors.HttpError as error:
        print(f"An error occured: {error}")

def readMessage(service):
    try:
        list_message_ID = getListOfMessageID(service)
        first_messageID = list_message_ID[0]        
        raw_message = service.users().messages().get(userId = 'me', id=first_messageID, format='raw').execute()
        raw_to_ASCII = base64.urlsafe_b64decode(raw_message['raw'].encode('ASCII'))
        ASCII_to_Bytes = email.message_from_bytes(raw_to_ASCII)
        content_maintype = ASCII_to_Bytes.get_content_maintype()

        if content_maintype == 'multipart':
            first_index, second_index = ASCII_to_Bytes.get_payload()
            print(first_index)
        else:
            print(f"Message's maintype is:{content_maintype}") 
    
    except errors.HttpError as error:
        print(f"An error occured:{error}")

def getListOfSender(service):
    try:
        message_id = getListOfMessageID(service)

        for everyID in message_id:
            message = service.users().messages().get(userId = 'me', id = everyID, format='raw').execute()
            message_to_ASCII = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
            ASCII_to_Bytes = email.message_from_bytes(message_to_ASCII)
            
            print(ASCII_to_Bytes['From'])           

    except errors.HttpError as error:
        print(f"An error occured: {error}")

def sendMessage(service):
    try:
        message_Body = 'Testing Gmail API. Please do not reply. Thank you!'
        mime_Message = MIMEMultipart()
        mime_Message['to'] = 'znrick22@gmail.com'
        mime_Message['subject'] = 'Testing 3'
        mime_Message.attach(MIMEText(message_Body, 'plain'))
        raw_String = base64.urlsafe_b64encode(mime_Message.as_bytes()).decode()
        message = service.users().messages().send(userId='me', body={'raw': raw_String}, media_mime_type=None,media_body=None).execute()
        return message  
    except errors.HttpError as error:
        print(f"An error occured: {error}")       

def searchSubject(service):
    try:
        search_String = input("Search subject: ")
        search_id = service.users().messages().list(userId = 'me', q = search_String).execute()
        num_of_results =search_id['resultSizeEstimate']

        subject_list = []

        if num_of_results == 0:
            print(f"No matches for \"{search_String}\" ")
            search_String = search_String.lstrip()
        else:
            list_of_messages = search_id['messages']

            for msg_id in list_of_messages:
                subject_list.append(msg_id['id'])
                

    except errors.HttpError as error:
        print(f"An error occured: {error}")

def getServices():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
   
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service
