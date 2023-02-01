from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import errors

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/postmaster.readonly']

def main():
    """Shows basic usage of the PostmasterTools v1beta1 API.
    Prints the visible domains on user's domain dashboard in https://postmaster.google.com/managedomains.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmailpostmastertools', 'v1beta1', credentials=creds)

    domains = service.domains().list().execute()
    if not domains:
        print('No domains found.')
    else:
        print('Domains:')
        for domain in domains['domains']:
            print(domain)


def get_domain(service, domain_name):
    """Gets a specific domain registered by the client.

    Args:
    service: Authorized Gmail PostmasterTools API instance.
    domain_name: The fully qualified domain name.

    Returns:
    The domain.
    """
    try:
      query = 'domains/' + domain_name
      domain = service.domains().get(name=query).execute();
      print(domain)
      return domain
    except errors.HttpError as err:
      print('An error occurred: %s' % err)



def list_domains(service):
    """Lists the domains that have been registered by the client.

    Args:
    service: Authorized Gmail PostmasterTools API instance.

    Returns:
    Response message for ListDomains.
    """
    try:
      domains = service.domains().list().execute()
      if not domains:
          print('No domains found.')
      else:
          print('Domains:')
          for domain in domains['domains']:
              print(domain)
      return domains
    except errors.HttpError as err:
      print('An error occurred: %s' % err)

def get_traffic_stats(service, domain_name, date):
    """Gets the traffic stats for a domain for a specific date.

  Args:
    service: Authorized Gmail PostmasterTools API instance.
    domain_name: The fully qualified domain name.
    date The date to get the domain traffic stats. Must be in "YYYYMMDD" format.

  Returns:
    The traffic stats of the domain for this date.
    """
    try:
        query = 'domains/%s/trafficStats/%s' %(domain_name,date)
        traffic_stats = service.domains().trafficStats().get(name=query).execute();
        print(traffic_stats);
        return traffic_stats;
    except errors.HttpError as err:
        print('An error occurred: %s' % err)
        
def list_traffic_stats(service, domain_name, date, page_size, page_token):
    """Gets the traffic stats for a domain for a specific date.

    Args:
    service: Authorized Gmail PostmasterTools API instance.
    domain_name: The fully qualified domain name.
    date The date to get the domain traffic stats. Must be in "YYYYMMDD" format.
    page_size The number of TrafficStats to get per request.
    page_token The nextPageToken value returned from a previous List request, if any.

    Returns:
    The traffic stats of the domain for this date.
    """
    try:
        query = 'domains/' + domain_name
        list_traffic_stats_response = service.domains().trafficStats().list(parent=query, pageSize=page_size, pageToken=page_token).execute();
        print(list_traffic_stats_response);
        return list_traffic_stats_response;
    except errors.HttpError as err:
        print('An error occurred: %s' % err)