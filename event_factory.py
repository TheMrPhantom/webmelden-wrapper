import uuid
from datetime import datetime, timedelta
import caldav
import uuid
import utils

class WebmeldenEvent:
    def __init__(self, event_data):
        self.state=''
        self.name=''
        self.date=''
        self.location=''
        self.judge=''
        self.club=''

        # Fill state attribute
        if event_data[0]=='Meldung angenommen':
            if event_data[29]=='Zahlung vollständig':
                self.state='paid'
            else:
                self.state='accepted'
        elif event_data[0]=='Meldung abgeschickt':
            self.state='registered'
        elif event_data[0]=='Meldung auf Warteliste':
            self.state='waiting'
        else:
            raise ValueError("Invalid event data, no state found")
        
        # Fill name attribute
        self.name=event_data[8]

        # Fill date attribute
        self.date=datetime.strptime(event_data[1], '%d.%m.%Y')

        # Fill location attribute
        self.location=event_data[3]

        # Fill judge attribute
        self.judge=event_data[4].replace('Richter: ','')

        # Fill club attribute
        self.club=event_data[15]
    
    def __str__(self):
        return f"{self.name}, {self.date.strftime('%d.%m.%Y')} -> {self.state}"

class EventFactory:

    def __init__(self):
        
        self.url = utils.caldav_url
        self.username = utils.caldav_username
        self.password = utils.caldav_password

        # Create a connection to the Nextcloud CalDAV server
        self.client = caldav.DAVClient(self.url, username=self.username, password=self.password)

        # Get the calendar (assuming you have two calendars)
        principal = self.client.principal()
        calendars = principal.calendars()
        
        # save 'Angenommene Turniere', 'Bezahlte Turniere' and 'Gemeldete Turniere' in variables. search for them in the list of calendars by name
        self.accepted_calendar = None
        self.paid_calendar = None
        self.registered_calendar = None
        self.waiting_calendar = None

        for calendar in calendars:
            if calendar.name == 'Turniere Gemeldet':
                self.registered_calendar = calendar
            elif calendar.name == 'Turniere Bezahlt':
                self.paid_calendar = calendar
            elif calendar.name == 'Turniere Angenommen':
                self.accepted_calendar = calendar 
            elif calendar.name == 'Turniere Warteliste':
                self.waiting_calendar = calendar

        if self.accepted_calendar is None or self.paid_calendar is None or self.registered_calendar is None or self.waiting_calendar is None:
            print("One or more calendars not found")
            exit()
        
        self.calendars = [self.accepted_calendar, self.paid_calendar, self.registered_calendar, self.waiting_calendar]
    
    def disconnect(self):
        self.client.close()
    
    def create_event(self, calendar_name:str, date: datetime, summary: str, description: str, location: str):
        # select the calendar
        if calendar_name == 'accepted':
            calendar = self.accepted_calendar
        elif calendar_name == 'paid':
            calendar = self.paid_calendar
        elif calendar_name == 'registered':
            calendar = self.registered_calendar
        elif calendar_name == 'waiting':
            calendar = self.waiting_calendar
        else:
            print("Invalid calendar")
            return
        
        # create the event string
        event_string = self.__build_event_string(date, summary, description, location)
        
        # save the event
        calendar.save_event(event_string)

        print("Event successfully created.")
    
    from typing import Tuple

    def find_event(self, name: str,date:datetime):
        # Search all calendars on the date for the event with the given name
        for calendar in self.calendars:
            events = calendar.date_search(date, date + timedelta(days=1))
            for event in events:
                if event.data.find(name) != -1:
                    return calendar, event
                
    def delete_event(self, name: str, date: datetime):
        self.find_event(name, date)[1].delete()
        print("Event successfully deleted.")
    
    def delete_all_events(self):
        for calendar in self.calendars:
            events = calendar.date_search(datetime.now(), datetime.now() + timedelta(days=365))
            for event in events:
                event.delete()
        print("All events successfully deleted.")
    
    def create_event_from_webmelden(self, event: WebmeldenEvent):
        # select the calendar
        if event.state == 'accepted':
            calendar = self.accepted_calendar
        elif event.state == 'paid':
            calendar = self.paid_calendar
        elif event.state == 'registered':
            calendar = self.registered_calendar
        elif event.state == 'waiting':
            calendar = self.waiting_calendar
        else:
            print("Invalid calendar")
            return
        
        # create the event string
        event_string = self.__build_event_string(event.date, event.name, f"Richter: {event.judge}\nVerein: {event.club}", event.location)
        
        # save the event
        calendar.save_event(event_string)
        
    
    def move_event(self, event, new_calendar_name: str):
        # select the calendar
        if new_calendar_name == 'accepted':
            calendar = self.accepted_calendar
        elif new_calendar_name == 'paid':
            calendar = self.paid_calendar
        elif new_calendar_name == 'registered':
            calendar = self.registered_calendar
        elif new_calendar_name == 'waiting':
            calendar = self.waiting_calendar
        else:
            print("Invalid calendar")
            return
        
        # move the event
        self.__move_calendar(event, calendar)
    

    def __build_event_string(self,date: datetime, summary: str, description: str, location: str) -> str:
        return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:{str(uuid.uuid4())}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}
DTSTART:{(date).strftime('%Y%m%d')}
DTEND:{(date + timedelta(days=1)).strftime('%Y%m%d')}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
END:VEVENT
END:VCALENDAR"""

    def __move_calendar(self, event, new_calendar):
        # Get the event data
        event_data = event.data

        # Create a new event in the destination calendar
        new_event = new_calendar.add_event(event_data)

        # Check if the new event is created successfully
        if new_event:
            # If the event is successfully copied, remove the event from the original calendar
            event.delete()
            print("Event successfully moved.")
        else:
            print("Failed to move the event.")


