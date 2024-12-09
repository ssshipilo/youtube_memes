import httplib2
import os
import random
import sys
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

import json
import pickle
import socket
import datetime
import requests
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from webdriver_manager.chrome import ChromeDriverManager

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def send_message_to_user(text: str):
    with open(os.path.join(os.getcwd(), 'core', 'settings.json'), 'r') as f:
        data_json = json.loads(f.read())

    token = data_json['telegram']['token_bot']
    chat_id = data_json['telegram']['my_chat_id']
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, data=data)
    return response.json()

def get_last_bot_message():
    with open(os.path.join(os.getcwd(), 'core', 'settings.json'), 'r') as f:
        data_json = json.loads(f.read())

    token = data_json['telegram']['token_bot']
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url)
    
    updates = response.json()['result']
    if not updates:
        return False

    last_message = None
    for update in updates:
        if 'message' in update:
            last_message = update['message']

    if last_message:
        timestamp = last_message['date']
        date = datetime.datetime.fromtimestamp(timestamp).date()
        today = datetime.datetime.now().date()
        
        if date == today:
            message = last_message.get('text', False)
            print(message)
            if message.startswith('http://localhost'):
                return message
            else:
                return False

    return False

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port

def write_input(element, text: str, delay=0.1):
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

def google_auth(use_bot=False, headless=True):

    with open(os.path.join(os.getcwd(), 'core', 'settings.json'), 'r') as f:
        data_json = json.loads(f.read())

    try:
        print(f'Starting to connect to Google')
        
        creds_pickle_path = os.path.join(os.getcwd(), 'core', 'google_auth', 'creds.pickle')
        print(creds_pickle_path)
        if os.path.exists(creds_pickle_path):
            with open(creds_pickle_path, 'rb') as f:
                creds = pickle.load(f)
        else:
            scopes = data_json['google']['youtube']['scopes']
            flow = InstalledAppFlow.from_client_secrets_file(os.path.join(os.getcwd(), 'core', 'google_auth', 'client_api.json'),  redirect_uri='http://localhost', scopes=scopes)
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            # [SERVER AUTH] Авторизация с помощью бота
            def auth_bot():
                send_message_to_user(auth_url)
                while True:
                    try:
                        time.sleep(1)
                        code = get_last_bot_message()
                        print(code)
                    except Exception as e:
                        print("[WAIT] Ожидаем код от меня")
                        continue

                    if code == "" or code == False or code == None:
                        print(code)
                        time.sleep(5)
                        continue
                    else:
                        send_message_to_user("Я получил код авторизации")
                        return code
                        break
            
            # [SERVER AUTH] Авторизация с помощью selenium+webdriver
            def auth_driver(auth_url):
                EMAIL = data_json['google']['email']
                PASSWORD = data_json['google']['password']

                print('[LOG] Открываем браузер')

                # CHROME
                chrome_driver = ChromeDriverManager().install()
                # or --------------------
                # chrome_driver = "./Drivers/chromedriver.exe"
                # https://googlechromelabs.github.io/chrome-for-testing/#stable

                service = Service(chrome_driver)
                service.start()

                ua = UserAgent()
                options = webdriver.ChromeOptions()
                options.add_argument("start-maximized")
                options.add_argument("--disable-dev-shm-usage")
                path_local = os.path.join(os.getcwd(), 'core', 'google_auth', 'cache')
                options.add_argument(f"--user-data-dir={path_local}")
                options.add_argument("--remote-debugging-port=" + str(get_free_port()))
                # options.add_argument("--incognito")
                options.add_argument("--lang=en-us")
                options.add_argument("--disable-web-security")
                options.add_argument("--allow-running-insecure-content")
                options.add_argument(f"--user-agent={ua.chrome}")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging", "disable-notifications"])
                options.add_experimental_option('useAutomationExtension', False)
                if headless:
                    options.add_argument("--headless")
                driver = webdriver.Chrome(service=service, options=options)

                driver.get('https://accounts.google.com/o/oauth2/auth/oauthchooseaccount?client_id=717762328687-iludtf96g1hinl76e4lc1b9a82g457nn.apps.googleusercontent.com&scope=profile%20email&redirect_uri=https%3A%2F%2Fstackauth.com%2Fauth%2Foauth2%2Fgoogle&state=%7B%22sid%22%3A609%2C%22st%22%3A%2259%3A3%3A1b8%2C16%3A5a495045abfe83f7%2C10%3A1700794996%2C16%3A31cde20abe0a0e4b%2C253904db31f93f3893a7725c83d3b1196a5fd614d9aaa701150a58f69ef6ea65%22%2C%22cid%22%3A%22717762328687-iludtf96g1hinl76e4lc1b9a82g457nn.apps.googleusercontent.com%22%2C%22k%22%3A%22Google%22%2C%22ses%22%3A%22a0b385ead3cc4849a317017aad67584d%22%7D&response_type=code&service=lso&o2v=1&theme=glif&flowName=GeneralOAuthFlow')
                time.sleep(3)
                current_url = ""

                def auth_data(driver):
                    # Email
                    input_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@type="email"]'))
                    )
                    # driver.execute_script("arguments[0].value = arguments[1];", input_element, EMAIL)
                    write_input(input_element, EMAIL)
                    input_element.send_keys(Keys.ENTER)
                    time.sleep(2)

                    # Password
                    input_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
                    )
                    # driver.execute_script("arguments[0].value = arguments[1];", input_element, PASSWORD)
                    write_input(input_element, PASSWORD)
                    input_element.send_keys(Keys.ENTER)

                def access_data(driver):
                    email_select = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f'//div[@data-identifier="{EMAIL}"]'))
                    )
                    driver.execute_script("arguments[0].click()", email_select)
                    time.sleep(5)
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(3)
                    actions.send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).send_keys(Keys.TAB).perform()
                    time.sleep(1)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(2)
                    current_url = driver.current_url
                    
                    return current_url
                
                while True:
                    try:
                        auth_data(driver)
                    except Exception as e:
                        driver.get(auth_url)
                        time.sleep(3)
                        try:
                            auth_data(driver)
                            current_url = access_data(driver)
                            if current_url != "":
                                    break
                            else:
                                continue
                        except:
                            try:
                                current_url = access_data(driver)
                                if current_url != "":
                                    break
                                else:
                                    continue
                            except Exception as e:
                                auth_driver(auth_url)
                                send_message_to_user("Ваше Величество авторизация Google странно затянулась. Требуеться Ваше вмешательство в работу программы!")
                                break

                print("[LOG] Completed!")
                return current_url
            
            if use_bot:
                code = auth_bot()
            else:
                code = auth_driver(auth_url)

            parsed_url = urlparse(code)
            query_params = parse_qs(parsed_url.query)
            code = query_params['code'][0]
            creds = flow.fetch_token(code=code)
            with open(os.path.join(os.getcwd(), 'core', 'google_auth', 'client_api.json'), 'r') as f:
                data_j = json.loads(f.read())
            creds['client_id'] = data_j['installed']['client_id']
            creds['client_secret'] = data_j['installed']['client_secret']
            creds = Credentials.from_authorized_user_info(info=creds)

            with open(creds_pickle_path, 'wb') as f:
                pickle.dump(creds, f)
            send_message_to_user("Google сессия успешно добавлена!")
            
        # ------------- YouTube -------------
        api_service_name    =   data_json['google']['youtube']['service_name']
        api_version         =   data_json['google']['youtube']['api_version']
        service_yt          =   build(api_service_name, api_version, credentials=creds)
        # ------------- YouTube -------------

        print(f'Accessed successfully')
        return {'youtube': service_yt}
    except Exception as e:
        print(e)
        google_auth()



# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

def initialize_upload(options):
  tags = None
  if options['keywords']:
    tags = options['keywords'].split(",")

  youtube = google_auth(False, True)
  insert_request = youtube['youtube'].videos().insert(
      part="snippet,status,liveStreamingDetails",
      body={
          "snippet": {
              "categoryId": "10",
              "description": options['description'],
              "title": options['title'],
              "tags": tags,
          },
          "status": {
              "privacyStatus": options['privacyStatus'],
              "selfDeclaredMadeForKids": False, 
          },
      },
      
      media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
  )
  # response = insert_request.execute()

  resumable_upload(insert_request)

def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print("Video id '%s' was successfully uploaded." % response['id'])
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except Exception as e:
      exit(f"A retriable HTTP error occurred:\n{e}")

    if error is not None:
      print(error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)

def upload_video(video_data):
  args = argparser.parse_args()
  if not os.path.exists(video_data['file']):
    exit("Please specify a valid file using the --file= parameter.")

  try:
    initialize_upload(video_data)
  except Exception as e:
    print(f"An HTTP error occurred:\n{e}")

if __name__ == '__main__':
    video_data = {
        "file": "video.mp4",
        "title": "Best of memes!",
        "description": "#shorts \n Giving you the hottest memes of the day with funny comments!",
        "keywords":"meme,reddit",
        "privacyStatus":"private"
    }
    upload_video(video_data)