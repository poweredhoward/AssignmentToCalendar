# https://developers.google.com/google-apps/calendar/v3/reference/events/insert

#A script to read a pdf from Elliot with meeting assignments and add them to Google calendar
from __future__ import print_function
import httplib2
import os
import PyPDF2
import re
import pprint

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'KH Assignments To Calendar'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

#Read pdf as raw text, split into dates/assignments, remove extra into
def getText(doc):
    pdfinput = PyPDF2.PdfFileReader(open(doc, 'rb'))
    pdftext = pdfinput.getPage(0).extractText()
    textsplit = re.split('(\d\d\/\d\d\/\d\d\d\d)', pdftext)
    del textsplit[0]
    del textsplit[0]
    del textsplit[-1]
    print(textsplit)
    return textsplit

#Give start date in acceptable format
def convertStartDate(date):
    newDate = datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    dateTime = newDate + 'T19:00:00-07:00'
    return dateTime

#Same as startDate, but sets ending time as 8pm
def convertEndDate(date):
    newDate = datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    dateTime = newDate + 'T20:00:00-07:00'
    return dateTime


def generateEvent(assignment, date):
    event = {
    'summary': 'Meeting: ' + assignment,
    'start': {
      'dateTime': convertStartDate(date),
      'timeZone': 'America/Los_Angeles',
    },
    'end': {
      'dateTime': convertEndDate(date),
      'timeZone': 'America/Los_Angeles',
    },
    'reminders': {
      'useDefault': False,
      'overrides': [
        {'method': 'popup', 'minutes': 1440},
      ],
    },
    }

    return event

def main():
   
    # docToRead = 'assignments updated 2.14.18.pdf'
    # docText = getText(docToRead)
    pp = pprint.PrettyPrinter(indent=4)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    #Get all assignments
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=30, singleEvents=True,
        orderBy='startTime', q='Meeting').execute()
    existingEvents = eventsResult.get('items', [])

    for e in existingEvents:
        pp.pprint(e)
    #Read through extracted, split text and create events for each assignment
    # for i in range(0, len(docText), 2):
    #     # i is the assignment name/summary, i+1 is the date
        
    #     event = generateEvent(docText[i], docText[i+1])
    #     event = service.events().insert(calendarId='primary', body=event).execute()
    #     print ('Event created: %s' % (event.get('htmlLink')))
           


if __name__ == '__main__':
    main()