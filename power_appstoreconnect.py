import uncurl
import requests
from rich.prompt import Prompt
from rich.console import Console
import os
import sys
import configparser
import re

TESTERS = "https://appstoreconnect.apple.com/iris/v1/sandboxTesters?limit=2000"
TEST = "https://appstoreconnect.apple.com/iris/v1/sandboxTesters?limit=1"
CREATE_SANDBOX = "https://appstoreconnect.apple.com/iris/v1/sandboxTesters"
DELETE = "https://appstoreconnect.apple.com/iris/v1/sandboxTesters/"

session = requests.Session()
console = Console()
config = configparser.ConfigParser()

## open file which contains curl
#with open("curl.txt") as data:
#    curl = data.read()
#
## get request data from curl
#request = uncurl.parse_context(curl)
#
## provide default data to the request methods
#session.headers.update(request.headers)
#session.cookies.update(request.cookies)
#
## GET testers account
#response = session.get(TESTERS)
#console.print(response.json())

# DELETE function

def delete_sandboxes():
    if not os.path.isfile("testers.json"):
        # get all records
        console.print("[green]Getting records...[/green]")
        response = session.get(TESTERS)
        if response.status_code == 200:
            data = response.json()
            with open('testers.json', 'w') as testers:
                testers.write(str(data))
        else:
            console.print("Something went wrong...", style="red bold")
            console.print(response.json())
    # parse file
    with open("testers.json") as data:
        testers = data.read()
        testers = eval(testers)
    dict_of_sandboxes = {user["attributes"]["email"]: user["id"] for user in testers["data"]}
    for email, user_id in dict_of_sandboxes.items():
        response = session.delete(f"{DELETE}{user_id}")
        if response.status_code == 204:
            console.print(f"✅ The next user: [purple]{email}[/purple] has been deleted")
        else:
            console.print("Something went wrong...", style="red bold")
            console.print(f"{response.json()}")


# FUNCTION post
def create_user(mask, amount, **kwargs):
   counter = re.search("(\d+)", mask).group()
   for i in range(int(amount)):
       counter = int(counter)
       counter += 1
       mask = re.sub("\d+", str(counter), mask)
       country = kwargs.get("country")
       if not country:
            country = "RUS"
# POST DATA
       DATA = {
             "data": {
                 "type": "sandboxTesters",
                 "attributes": {
                     "email": mask,
                     "firstName": "QA",
                     "lastName": "New",
                     "password": "q12345678Q",
                     "confirmPassword": "q12345678Q",
                     "secretQuestion": "S    tart sdf ",
                     "secretAnswer": "dasd sdf sdf",
                     "appStoreTerritory": country,
                     "birthDate": "1980-02-16"
                 }
             }
                }
       response = session.post(CREATE_SANDBOX, json=DATA)
       if response.status_code == 201:
           console.print(f"✅ The next account has been created [bold magenta]{mask}[/bold magenta]")
           config.set("CREATION", "mask", mask)
       else:
           console.print("Something went wrong...", style="red bold")
           console.print(response.json())



# check if curl file is not exists
if not os.path.isfile("curl.txt"):
    console.print("File curl.txt can't be found", style="red bold")
    sys.exit()


# open file which contains curl
with open("curl.txt") as data:
    curl = data.read()
# get request data from curl
request = uncurl.parse_context(curl)

# provide default data to the request methods
session.headers.update(request.headers)
session.cookies.update(request.cookies)

# Make a test that everything ok
with console.status("Verifying that everything ok...", spinner="hearts"):
    response = session.get(TEST)
# check status code
if response.status_code == 200:
    console.print("You are lucky!", style="green bold")
else:
    console.print("Something went wrong...", style="red bold")
    console.print(response.json())
    sys.exit()

# every time script, supposued it's not first time
file_is_not_exists = False
# check if config file is not exists
if not os.path.isfile("config.ini"):
    console.print("File config.ini can't be found, it will be created", style="yellow bold")
    file_is_not_exists = True
# create config
    counter = ""
    while not counter:
        mask = Prompt.ask("Please, type desired mask",default="qa_0@mybook.ru")
        counter = re.search("(\d+)", mask).group()
    config.add_section("CREATION")
    config.set("CREATION", "mask", mask)
# Writing our configuration file to 'config.ini'
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# read config file
config.read('config.ini')
mask = config.get("CREATION", "mask")
if not file_is_not_exists:
    console.print(f"The last created sandbox: [bold magenta]{mask}[/bold magenta]")
# ask user about amount of accounts
console.print("[bold blue]Examples[/bold blue]: 1, 10 RUS, 3 EST (you can choose a country)")
amount = Prompt.ask("Please type desired amount of sandboxes that will be created", default="1").upper()
# get country code if it presents
list_of_values = amount.split()
amount = list_of_values[0]
if len(list_of_values) > 1 and list_of_values[0] != "DELETE":
    country = list_of_values[1]
if list_of_values[0] == "DELETE":
# delte all records
    console.print("⚛️  [bold red]WARNING[/bold red] all sandboxes will be deleted")
    with console.status("Please, wait", spinner="hearts"):
        delete_sandboxes()


else:
# create desired amount of sandboxes
    with console.status("Sandboxes are being creating", spinner="hearts"):
        console.print(f"The next amount of sandboxes will be created: {amount}")
        if len(list_of_values) > 1:
            create_user(mask, amount, country=country)
        else:
            create_user(mask, amount)
# Writing our chages file to 'config.ini'
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
