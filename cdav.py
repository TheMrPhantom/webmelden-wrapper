import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import event_factory
import utils

def get_caldav_events():
    # Create a session to persist cookies
    session = requests.Session()

    # URL of the login page (modify as needed)
    login_url = "https://www.webmelden.de/index.php"

    # Data required for login (check HTML form field names)
    payload = {
        "starteruser": utils.webmelden_username,
        "starterpassword": utils.webmelden_password,
        "starterlogin": "einloggen"
    }

    # Send POST request to login
    response = session.post(login_url, data=payload, allow_redirects=True)
    php_session_id = session.cookies["PHPSESSID"]

    # Check if login was successful by verifying session cookie
    if "PHPSESSID" in session.cookies.get_dict():
        print("Login successful! PHPSESSID:", session.cookies["PHPSESSID"])
    else:
        print("Login failed!")

    # Extract query params from the final redirected URL
    parsed_url = urlparse(response.url)  # Parse URL components
    query_params = parse_qs(parsed_url.query)  # Convert to dictionary

    # Print the final URL and query parameters
    print("Redirected URL:", response.url)
    print("Query Parameters:", query_params)


    # Now access a protected page
    protected_url = f"https://www.webmelden.de/meldeuebersicht.php?id={query_params['id'][0]}"
    protected_response = session.get(protected_url,cookies=session.cookies)

    # Print or process the page content


    soup = BeautifulSoup(protected_response.text, "lxml")  # or "html.parser"

    # Find all table rows with class "oddtr hover"
    rows = soup.find_all("tr")
    row_data = []
    for row in rows[5:-4]:
        tds = row.find_all("td")  # Get all <td> elements
        first_td_title = tds[0].get("title", "") if tds else ""  # Extract title of first <td>
        row_text = list(row.stripped_strings)  # Extract full row text as a list
        row_data.append([first_td_title] + row_text)  # Add title separately
        # Print row text

    # convert row to webmelden events
    events = []
    for row in row_data:
        e=event_factory.WebmeldenEvent(row)
        events.append(e)
        print("Converted:",e)
    
    return events