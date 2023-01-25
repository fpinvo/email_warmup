
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
import traceback

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = 'farhan.pirzada@invozone.com'
# setting up db

db = Warmup_data()
source_email_data = None
target_email_data = None

def check_token(tb_name,email):
    return db.select_all("Select * from "+tb_name+" where email = '"+email+"'")

def create_token(table_name, email, pickled_creds, esp='gmail'):
    time = datetime.datetime.now()
    query = f'INSERT INTO {table_name} (email, e_type, pickle, create_at) VALUES ("{email}", "{esp}", {pickled_creds}, "{time}");'
    print(f'create_token:::::{query}::::')
    db.commit(query)

def update_token(table_name, email, pickled_data):
    time = datetime.datetime.now()
    query = f'UPDATE {table_name} SET pickle = {pickled_data}, update_at = "{time}" WHERE email = "{email}";'
    print(f'update_token:::::{query}::::')
    db.commit(query) 

        

# def main(tb_name,email):
#     global our_email,source_email_data,target_email_data
#     """Shows basic usage of the Gmail API.
#     Lists the user's Gmail labels.
#     """
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     print(email)
#     source_email_data = check_token(tb_name,email)
#     target_email_data = check_token('target','farhan.pirzada@invozone.com')
#     print(target_email_data)
#     our_email = source_email_data[0][2]
#     if source_email_data[0][7]:
#         # db.execute("Update source set token ="+ +"")
#         creds = Credentials.from_authorized_user_file(str(source_email_data[0][7]), SCOPES)
#     # if os.path.exists('token.json'):
#     #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         # with open('token.json', 'w') as token:
#         #     print(" file token.json stores")
#         #     print(creds.to_json())
#         #     token.write(creds.to_json())
#         print("updating the db")
#         print("UPDATE source SET token ='"+creds.to_json()+"' where email ='"+email+"'")
#         db.execute("Insert source values('"+creds.to_json()+"' where email ='"+email+"'")
        

#     try:
#         # Call the Gmail API
#         service = build('gmail', 'v1', credentials=creds)
#         results = service.users().labels().list(userId='me').execute()
#         labels = results.get('labels', [])

#         if not labels:
#             print('No labels found.')
#             return
#         print('Labels:')
#         for label in labels:
#             print(label['name'])

#     except HttpError as error:
#         # TODO(developer) - Handle errors from gmail API.

#         print(f'An error occurred: {error}')

def authenticate_user(email_obj):
    # global our_email,source_email_data,target_email_data 
    creds = None
    print(email_obj)

    # source_email_data = check_token(tb_name,email)
    # target_email_data = check_token('target','farhan.pirzada@invozone.com')
    # our_email = source_email_data[0][2]
    # # the file token.pickle stores the user's access and refresh tokens, and is
    # # created automatically when the authorization flow completes for the first time
    # if os.path.exists("token.pickle"):
    #     with open("token.pickle", "rb") as token:
    #         creds = pickle.load(token)
    #         print("file token.pickle")
    #         print(creds)
    # # if there are no (valid) credentials availablle, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    # save the credentials for the next run
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)
    # return build('gmail', 'v1', credentials=creds)
    service = build('gmail', 'v1', credentials=creds)
    try:
        email = email_obj[0][2]
        token = email_obj[0][6]
        if token:
            print('Token found')
        breakpoint()
        # store authenticated user token to DB
        with open('token.pickle', 'rb') as file:
            user_data = file.read()
        if token:
            print('update_token_call')
            update_token('source', email, user_data)
        else:
            create_token('source', email, user_data)
        return service
    except Exception as e:
        print(e)
        traceback.print_exc()


def create_service(creds):
    try:
        if not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        raise e
    
def get_user_service(user_email, tb_name='source'):
    """_summary_

    Args:
        user_email (_type_): _description_
    
    Returns:
        _type_: _description_
    """
    try:
        
            # import pdb; pdb.set_trace()
            source = check_token(tb_name, user_email)
            # print('SourceMail obj found')
            print(f'::::::::: Source_obj--> {source[0]}:::::::::')
            try:
                creds = pickle.loads(source[0][6])
                return create_service(creds)
            except:
                return authenticate_user(source)
                     
    except Exception as e:
        print(e)
        traceback.print_exc()



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
    db.commit("Insert into gmailThreadId values (NULL,'"+str(send_message["id"])+"','"+str(send_message["threadId"])+"','"+str(source_email_data[0][0])+"')",[])
    db.commit("Insert into campaign values (NULL,'"+str(target_email_data[0][0])+"','"+str(datetime.datetime.now())+"','"+str(datetime.datetime.now())+"',1,'"+str(db.cursor_.lastrowid)+"','"+str(source_email_data[0][0])+"')",[])
    return send_message


def show_chatty_threads(service):
    """Display threads with long conversations(>= 3 messages)
    Return: None

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    try:
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

def get_msg_headers(service,email_id):
    data = dict()
    msg = service.users().messages().get(userId="me", id=email_id, format="full").execute()
    if msg:
        data['snippet'] = msg['snippet']
        headers = msg['payload'].get("headers")
        print(headers)
        for header in headers:
            if header['name'] == 'Message-ID' or "Message-Id":
                data['Message-ID'] = header.get("value")
            if header['name'] == 'From' or 'from':
                data['From'] = header.get("value")
            if header['name'] == 'To' or 'to':
                data['To'] = header.get("value")
            if header['name'] == 'Subject' or 'subject':
                data['Subject'] = header.get("value")
            if header['name'] == 'Date':
                data['Date'] = header.get("value")
            if header['name'] == 'Content-Type':
                data['Content-Type'] = header.get("value")
        return data
    return None

def get_thread(service, email_id=None, thread_id=None):
    if email_id is not None:
        msg = service.users().messages().get(userId="me", id=email_id, format="full").execute()
        thread_id = msg['threadId']
    
    thread = service.users().threads().get(userId='me', id=thread_id).execute()
    thread_msgs = thread['messages']
#     print(type(thread_msgs))
#     print(len(thread_msgs))
    messages = dict()
#     print(thread_msgs)
    for idx, msg in enumerate(thread_msgs):
        messages[idx] = {}
        messages[idx]['snippet'] = msg['snippet']
        headers = msg['payload'].get("headers")
    #     print(headers)
        for header in headers:
            if header['name'] == 'Message-ID':
                messages[idx]['Message-ID'] = header.get("value")
            if header['name'] == 'From':
                messages[idx]['From'] = header.get("value")
            if header['name'] == 'To':
                messages[idx]['To'] = header.get("value")
            if header['name'] == 'Subject':
                messages[idx]['Subject'] = header.get("value")
            if header['name'] == 'Date':
                messages[idx]['Date'] = header.get("value")
            if header['name'] == 'Content-Type':
                messages[idx]['Content-Type'] = header.get("value")
        return messages


if __name__ == '__main__':
    # main()
    # get the Gmail API service

    # service = authenticate_user() 
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
    email = 'invozone.ht@gmail.com'
    data = check_token('source', email)
    # print(data)
    print(data[0])