
from __future__ import print_function

import os.path
import os
import pickle
# Gmail API utils
import google.auth
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
from connection import Warmup_data
import datetime

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = 'farhan.pirzada@invozone.com'
# setting up db

db = Warmup_data()
source_email_data = None
target_email_data = None

def check_token(tb_name,email):
    return db.select_all("Select * from "+tb_name+" where email = '"+email+"'")
    

def main(tb_name,email):
    global our_email,source_email_data 
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    print(email)
    source_email_data = check_token(tb_name,email)
    target_email_data = check_token('target','farhan.pirzada@invozone.com')
    our_email = source_email_data[0][2]
    if source_email_data[0][7]:
        # db.execute("Update source set token ="+ +"")
        creds = Credentials.from_authorized_user_file(str(source_email_data[0][7]), SCOPES)
    # if os.path.exists('token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        # with open('token.json', 'w') as token:
        #     print(" file token.json stores")
        #     print(creds.to_json())
        #     token.write(creds.to_json())
        print("updating the db")
        print("UPDATE source SET token ='"+creds.to_json()+"' where email ='"+email+"'")
        db.execute("Insert source values('"+creds.to_json()+"' where email ='"+email+"'")
        

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.

        print(f'An error occurred: {error}')

def authenticate_user(tb_name,email):
    global our_email,source_email_data 
    creds = None
    print(email)

    source_email_data = check_token(tb_name,email)
    target_email_data = check_token('target','farhan.pirzada@invozone.com')
    our_email = source_email_data[0][2]
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
            print("file token.pickle")
            print(creds)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # save the credentials for the next run
        # with open("token.pickle", "wb") as token:
        #     print("file token.pickle stores")
        #     print(creds, token)
        #     pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)



# Add the attachment with the given filename to the given message
def add_email_attachment(message, filename):
    content_type, encoding = guess_mime_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(filename, 'rb')
        msg = MIMEText(fp.read().decode(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(filename, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(filename, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(filename, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(filename)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)
    
def create_message(destination, obj, body, attachments=[]):
    if not attachments: # no attachments given
        message = MIMEText(body)
        message['to'] = destination
        message['from'] = our_email
        message['subject'] = obj
    else:
        message = MIMEMultipart()
        message['to'] = destination
        message['from'] = our_email
        message['subject'] = obj
        message.attach(MIMEText(body))
        for filename in attachments:
            add_email_attachment(message, filename)
    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, destination, obj, body, attachments=[]):
    send_message = service.users().messages().send(
      userId="me",
      body=create_message(destination, obj, body, attachments)
    ).execute()
    print(F'Message Id: {send_message["id"]}')
    # send_message["id"]
    # send_message["threadId"]
    print("Insert into gmailThreadId values(NULL,'"+str(send_message["id"])+"','"+str(send_message["threadId"])+"','"+str(source_email_data[0][0])+"')")
    db.execute("Insert into gmailThreadId values(NULL,'"+str(send_message["id"])+"','"+str(send_message["threadId"])+"','"+str(source_email_data[0][0])+"')")
    print(db.cursor_.lastrowid)
    print("Insert into campaign values(NULL,'"+target_email_data[0][0]+"','"+datetime.datetime.now()+"','"+datetime.datetime.now()+"','"+db.cursor_.lastrowid+"','"+source_email_data[0][0]+"'")
    db.execute("Insert into campaign values(NULL,'"+target_email_data[0][0]+"','"+datetime.datetime.now()+"','"+datetime.datetime.now()+"','"+db.cursor_.lastrowid+"','"+source_email_data[0][0]+"'")
    return send_message


def show_chatty_threads():
    """Display threads with long conversations(>= 3 messages)
    Return: None

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    try:
        # create gmail api client
        service = authenticate_user()

        # pylint: disable=maybe-no-member
        # pylint: disable:R1710
        # messages = service.users().messages().list(userId='me').execute().get('messages', [])
        # print(messages)

        threads = service.users().threads().list(userId='me').execute().get('threads', [])
        print(threads)
#         for thread in threads:
#             tdata = service.users().threads().get(userId='me', id=thread['id']).execute()
# #             print(f'Thread data:::::{tdata}')
#             nmsgs = len(tdata['messages'])
#             print(nmsgs)

#             # skip if <3 msgs in thread
#             if nmsgs > 2:
#                 msg = tdata['messages'][0]['payload']
#                 subject = ''
#                 for header in msg['headers']:
#                     if header['name'] == 'Subject':
#                         subject = header['value']
#                         break
#                 if subject:  # skip if no Subject line
#                     print(F'- {subject}, {nmsgs}')
#         return threads

    except HttpError as error:
        print(F'An error occurred: {error}')

def create_thread_message(to, subject, body, reply_to, thread_id, message_id):
    message = MIMEText(body, 'html')
    message['to'] = to
    message['from'] = our_email
    message['subject'] = f'Re: {subject}'

    if reply_to:
#         message['threadId'] = thread_id
        
        message['In-Reply-To'] = message_id
        message['References'] = message_id

        return {'raw': urlsafe_b64encode(message.as_bytes()).decode(), 'threadId': thread_id}

    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

def send_message_thread(service, destination, subject, body, thread_id,msg_id_3):
    return service.users().messages().send(
      userId="me",
      body=create_thread_message(destination,subject, body, True, thread_id, msg_id_3)
    ).execute()

def get_msg_id_header(service,email_id):
    data = dict()
    msg = service.users().messages().get(userId="me", id=email_id, format="full").execute()
    data['snippet'] = msg['snippet']
    headers = msg['payload'].get("headers")
#     print(headers)
    for header in headers:
        if header['name'] == 'Message-ID':
            data['Message-ID'] = header.get("value") 
            return data
    return None
    
if __name__ == '__main__':
    main()
    # get the Gmail API service

    service = authenticate_user() 
    # msg = send_message(service, "furqanaz456@gmail.com", "Hey 2",
    #         "Message Sent 2.")
    # print(msg)  
    # threads =show_chatty_threads()s
    
#     msg_id_3 = "CAHhPNieP_cd6pnoTywJSKQiFBazd5LFf57tLsf6Hi+vUCH6RjQ@mail.gmail.com"
#     msg_id_2 = 'CAAaKeg4Y+QWP5JxVQ4iRDyhG9HL2jYZVVPjDRRGzO_zZytkFVQ@mail.gmail.com'
#     msg_id_1 = "<CAAyL=gRO4f5P2=DD2qf_aG934iuS9U92ifZTZAb2ngsBCWTTvg@mail.gmail.com>"
#     # msg_id_1 = "<CAAyL=gSXSWkk32xZgzn-jvc5UQeXOEMLppo7GG0JyScev_Jj9A@mail.gmail.com>"
#     thread_id = "185be689883507d1"
#     send_message_thread(service, "furqanaz456@gmail.com", "Hey 2", 
#             """
#             reply to it third <br>
            
#             ----
# From: farhan.pirzada@invozone.com
# Date: Mon, 16 Jan 2023 22:26:43 -0800
# Message-ID: <CAAyL=gRO4f5P2=DD2qf_aG934iuS9U92ifZTZAb2ngsBCWTTvg@mail.gmail.com>
# Subject: Hey 2
# To: furqanaz456@gmail.com
# Content-Type: text/plain; charset="UTF-8"

# Message Sent 2.
# ----
# """, thread_id, msg_id_1)

