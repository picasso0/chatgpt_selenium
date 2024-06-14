from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# import chromedriver_autoinstaller
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import time
import socket
import threading
import os
import sys
import ssl
import json
from io import StringIO

class ChatGPTAutomator:

    def __init__(self, login_check=True, wait_sec=60, driver_path=None, chrome_path=None):
        """
        :param wait_sec: waiting for chatgpt response time
        """ 
        ssl._create_default_https_context = ssl._create_unverified_context
        self.chrome_path = chrome_path if chrome_path else self.get_chrome_path()
        # self.chrome_driver_path = ChromeDriverManager().install()
        self.chrome_driver_path = driver_path if driver_path != None else ChromeDriverManager().install()

        self.wait_sec = wait_sec
        self.login_check = login_check

        self.chrome_thread = None

        url = "https://chat.openai.com"
        free_port = self.find_available_port()
        self.start_remote_chrome(free_port, url)
        self.wait_for_human_verification()
        self.driver = self.setup_webdriver(free_port)
        self.driver.get(url)
        try:
            time.sleep(3)
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
            try:
                dialog_btn = self.driver.find_element(by=By.CSS_SELECTOR, value='[id^="radix-"] button')
                dialog_btn.click()
            except:
                pass
        except:
            time.sleep(5)

    def get_chrome_path(self):
        platform = sys.platform
        if platform == "win32":
            # Usually located at this path on Windows
            possible_paths = [
                r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"',
                r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'
            ]
            chrome_path = possible_paths[0] if os.path.exists(possible_paths[0].strip("\"")) else possible_paths[1]
        elif platform == "darwin":
            # Usually located at this path on macOS
            chrome_path = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
        else:
            # On Linux, 'google-chrome' is usually available in the PATH.
            chrome_path = "google-chrome"
        
        return chrome_path

    def find_available_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def start_remote_chrome(self, port, url):
        def open_chrome():
            profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "remote-profile") if sys.platform == "win32" else "remote-profile" 
            chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} --user-data-dir={profile_dir} {url}"
            os.system(chrome_cmd)

        self.chrome_thread = threading.Thread(target=open_chrome)
        self.chrome_thread.start()

    def setup_webdriver(self, port):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        try:
            driver = webdriver.Chrome(service=ChromeService(self.chrome_driver_path), options=chrome_options)
        except TypeError:
            try:
                driver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=chrome_options)
            except:
                if (Path.cwd() / self.chrome_driver_path).exists():
                    driver = webdriver.Chrome(executable_path=str(Path.cwd() / self.chrome_driver_path), options=chrome_options)
        except:
            if (Path.cwd() / self.chrome_driver_path).exists():
                driver = webdriver.Chrome(service=ChromeService(str(Path.cwd() / self.chrome_driver_path)), options=chrome_options)
        return driver

    def talk_to_chatgpt(self, prompt, to_list=False, to_csv=False, new_chat=False):
        if new_chat:
            try:
                self.driver.find_element(by=By.CSS_SELECTOR, value="nav>div:nth-child(1)>span:last-child>button").click()
                time.sleep(0.5)
                WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, "(//form//button[@disabled])[last()]")))
                WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
            except:
                pass
        self.send_prompt_to_chatgpt(prompt)
        if to_list or to_csv:
            return self.return_last_table(to_csv)
        else:
            return self.return_last_response()

    def send_prompt_to_chatgpt(self, prompt):
        input_box = self.driver.find_element(by=By.CSS_SELECTOR, value="form textarea")
        # prompt = prompt.replace("\n","\\n").replace("\'","\\\'")
        prompt_escaped = json.dumps(prompt).strip("\"").replace("'", "\\'").replace('"', '\\"')
        self.driver.execute_script(f"arguments[0].value = '{prompt_escaped}';", input_box)
        time.sleep(0.3)
        input_box.send_keys(Keys.ENTER)
        try:
            # input_btn = self.driver.find_element(by=By.CSS_SELECTOR, value="form div+button")
            input_btn = input_box.find_element(By.XPATH, '../following-sibling::button')
            time.sleep(0.1)
            input_btn.click()
        except:
            pass
        # time.sleep(self.wait_sec)
        try:
            # WebDriverWait(self.driver, self.wait_sec).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form button>[data-state=\"closed\"]")))
            WebDriverWait(self.driver, self.wait_sec).until(EC.visibility_of_element_located((By.XPATH, "(//form//button[@disabled])[last()]")))
        except:
            time.sleep(self.wait_sec)
            return
    def return_chatgpt_conversation(self):
        return self.driver.find_elements(by=By.CSS_SELECTOR, value='main div[data-message-author-role="assistant"]')

    def save_conversation(self, file_name):
        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        delimiter = "|＠|"
        chatgpt_conversation = self.return_chatgpt_conversation()
        with open(os.path.join(directory_name, file_name), "a") as file:
            for i in range(0, len(chatgpt_conversation), 2):
                file.write(
                    f"prompt: {chatgpt_conversation[i].text}\nresponse: {chatgpt_conversation[i + 1].text}\n\n{delimiter}\n\n")

    def return_last_response(self):
        """ :return: the text of the last chatgpt response """
        try:
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'main div[data-message-author-role="assistant"]')))
            response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='main div[data-message-author-role="assistant"]')
            if response_elements:
                return response_elements[-1].text
            else:
                return ""
        except:
            return ""
    def return_last_table(self, to_csv):
        def quote_field(field):
            if ',' in field or '\n' in field:
                return f'"{field}"'
            return field
        def table_to_list(table_element):
            rows = table_element.find_elements(by=By.CSS_SELECTOR, value='tr')
            table_data = []
            for row in rows:
                columns = row.find_elements(by=By.CSS_SELECTOR, value='th,td')
                row_data = [col.text for col in columns]
                table_data.append(row_data)
            return table_data
        try:
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'main div[data-message-author-role="assistant"]')))
            response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='main div[data-message-author-role="assistant"]')
            table_element = response_elements[-1].find_element(by=By.CSS_SELECTOR, value='div>table')
            if table_element:
                table_data = table_to_list(table_element)
                return StringIO("\n".join([",".join([quote_field(cell) for cell in row]) for row in table_data])) if to_csv else table_data
            else:
                return self.return_last_response()
        except:
            try:
                code_content = response_elements[-1].find_element(by=By.CSS_SELECTOR, value='div>code').text
                rows = code_content.split("\n")
                table = []
                for row in rows:
                    # Split by '|' to get the cells
                    cells = [cell.strip() for cell in row.split("|") if cell.strip()]
                # Skip rows that don't have data
                if len(cells) > 1:
                    table.append(cells)
                return table
            except:
                return self.return_last_response()
        
    def wait_for_human_verification(self):
        if not self.login_check:
            try:
                WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
            except:
                time.sleep(2)
            return
        print("Please complete the login or human verification steps if required.")
        while True:
            user_input = input(
                "Press 'y' once you've finished the login or human verification, or 'n' to review again:").lower()

            if user_input == 'y':
                print("Proceeding with the automated steps...")
                break
            elif user_input == 'n':
                print("Please finish the human verification. Waiting for completion...")
                time.sleep(5)  # You can adjust the waiting time as needed
            else:
                print("Incorrect input. Please enter 'y' or 'n'.")
        try:
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
        except:
            time.sleep(2)
        return
    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        self.driver.close()
        print("driver.close()")
        self.driver.quit()
        print("driver.quit()")
        sys.exit()
        print("sys.exit()")