#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Downloade zuerst die credentials.json von folgender Seite: https://developers.google.com/calendar/quickstart/python
# Klicke auf den Button "Enable the Google Calendar API" und dann auf "Download Client Configuration"
# Verschiebe die Datei in den gleichen Ordner wie die 3 Scripte.

# Wenn die Einträge nicht im Google Standard Kalender erstellt werden sollen, muss überall der Wert von calendarId=primary mit der ID des gewünschten Kalenders ersetzt werden. Siehe Ausgabe.

# 1 = OutlookzuGoogle
# 2 = Google zu Outlook

try:
    try:
        import os
        import datetime
        import pickle
        import codecs
        import requests
        import os.path
        import sys
        import time
        import webbrowser
        import csv, pytz
        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ModuleNotFoundError:
        print("Fehlende Pakete werden installiert...\n\n\n")
        os.system("pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib datetime requests python-csv pytz")
        print("\n\nBitte Script neustarten!")
        exit()

    # Lösche Konsoleninhalt...
    print("\033c", end="")
    os.system("clear||cls")
    os.system("printf '\e[8;50;125t'||mode con:lines=50 cols=125")

    try:
        import httplib
    except:
        import http.client as httplib

    # Teste Internet Verbindung
    def have_internet():
        conn = httplib.HTTPConnection("www.google.com", timeout=2)
        try:
            conn.request("HEAD", "/")
            conn.close()
            return True
        except:
            conn.close()
            print("Keine Internet Verbindung!")
            exit()
            return False

    have_internet()
    

    SCOPES = ['https://www.googleapis.com/auth/calendar.events','https://www.googleapis.com/auth/calendar']   


    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print("\nDu hast vergessen die Datei credentials.json herunterzuladen!\n\nBitte auf folgender Website den Button 'Enable the Google Calender API' drücken.")
                time.sleep(3)
                url = "https://developers.google.com/calendar/quickstart/python"
                webbrowser.open(url)
                exit(1)
        # Speichere Zugangsdaten in Datei
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            cal_summary = calendar_list_entry['summary']
            cal_id = calendar_list_entry['id']
            print("Kalender " +  cal_summary + " hat folgende ID: " + cal_id, end='\n')
            page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    now = datetime.datetime.now(pytz.timezone('Europe/Berlin')).isoformat()

    if (sys.argv[1]) == "1":
        print("Outlook Kalender Einträge werden nach Google Kalender gesynct")
        # Importiere CSV
        try:
            import codecs
            BLOCKSIZE = 1048576
            with codecs.open('events.csv', "r", "utf-8") as sourceFile:
                with codecs.open('events2.csv', "w", "utf-16") as targetFile:
                    while True:
                        contents = sourceFile.read(BLOCKSIZE)
                        if not contents:
                            break
                        targetFile.write(contents)

            with open('events2.csv', encoding='utf-16') as csvfile:
                readCSV = csv.reader(csvfile, delimiter=';')
                for row in readCSV:
                    Subject = row[0]
                    StartDate = row[1] + "_" + row[2]
                    EndDate = row[3] + "_" + row[4]
                    AllDayEvent = row[5]
                    Description = row[6]
                    Location = row[7]

                    StartDate_n = datetime.datetime.strptime(StartDate, '%m/%d/%Y_%H:%M:%S')
                    StartDate_n = StartDate_n.isoformat()

                    # Rufe die Google Kalender API auf
                    print('Suche nach Termin...')
                    events_result = service.events().list(calendarId='primary', timeMin=StartDate_n+"+01:00",
                                                        maxResults=1, singleEvents=True,
                                                        orderBy='startTime', q=Subject).execute()
                    events = events_result.get('items', [])

                    if not events:

                        EndDate_n = datetime.datetime.strptime(EndDate, '%m/%d/%Y_%H:%M:%S')
                        EndDate_n = EndDate_n.isoformat()

                        event = {
                        'summary': Subject,
                        'location': Location,
                        'description': Description,
                        'start': {
                            'dateTime': StartDate_n,
                            'timeZone': 'Europe/Berlin',
                        },
                        'end': {
                            'dateTime': EndDate_n,
                            'timeZone': 'Europe/Berlin',
                    #    },
                    #    'recurrence': [
                    #        'RRULE:FREQ=DAILY;COUNT=2'
                    #    ],
                    #    'attendees': [
                    #        {'email': 'lpage@example.com'},
                    #        {'email': 'sbrin@example.com'},
                    #    ],
                    #    'reminders': {
                    #        'useDefault': False,
                    #        'overrides': [
                    #        {'method': 'email', 'minutes': 24 * 60},
                    #        {'method': 'popup', 'minutes': 10},
                    #        ],
                        },
                        }

                        event = service.events().insert(calendarId='primary', body=event).execute()
                        print("Termin " + Subject + " erstellt")
                    for event in events:
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        print("Termin gefunden: " + start, event['summary'])
            csvfile.close()

        except FileNotFoundError:
            print("\nKeine CSV Datei gefunden! Evtl. wurden in Outlook keine Termine gefunden oder das PowerShell Script wurde nicht gestartet!\n")
            exit(1)

        os.remove("events.csv")
        os.remove("events2.csv")


    elif (sys.argv[1]) == "2":
        print("Google Kalender Einträge werden nach Outlook Kalender gesynct")

        # Rufe Kalender API auf
        now = datetime.datetime.now(pytz.timezone('Europe/Berlin')).isoformat()

        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=1000, singleEvents=True,
                                            orderBy='startTime').execute()

        events = events_result.get('items', [])

        try:
            os.remove("events.csv")
        except FileNotFoundError:
            pass
        with codecs.open("events.csv", "w", encoding='utf-8') as f:
            f.write("Subject;StartDate;EndDate;AllDayEvent;Description;Location\r\n")
            f.close()

        if not events:
            print('Keine Termine gefunden.')

        for event in events:
            if event['start'].get('dateTime') == None:
                alldayevent = "true"
            else:
                alldayevent = "false"
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            description = event.get('description')
            if description is None:
                description = ""
            location = event.get('location')
            if location is None:
                location = ""

            g_events=(event['summary'] + ";" + start + ";" + end + ";" + str(alldayevent) + ";" + str(description) + ";" + str(location) + "\r\n")

            f = open("events.csv", "a", encoding='utf-8')
            f.write(g_events)

        f.close()

except KeyboardInterrupt:
    print("Programm wird beendet...")
    try:
        os.remove("events.csv")
        os.remove("events2.csv")
    except FileNotFoundError:
        pass
