import event_factory
import cdav
import schedule
import time

def import_webmelden_events():
    try:
        events = cdav.get_caldav_events()

        # create events in calendar
        factory = event_factory.EventFactory()
        factory.delete_all_events()

        try:
            for event in events:
                factory.create_event_from_webmelden(event)
                print("Created event:", event)
        except:
            print("Error creating events")
        factory.disconnect()
    except Exception as e:
        print(e)

import_webmelden_events()

schedule.every(60*3).minutes.do(import_webmelden_events)

while True:
    time.sleep(5*60)
    schedule.run_pending()



