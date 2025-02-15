from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import random
from selenium.webdriver.common.action_chains import ActionChains
# from selenium_stealth import stealth
from pathlib import Path
import time
import os
import ssl
import json
from io import StringIO
from fake_useragent import UserAgent
from utils import download_file, extract_zip
from global_vars import USERDATA_ZIP_DOWNLOAD_DIRECTORY

class ChatGPTAutomator:
    def __init__(self):
        pass
    async def initialize(self, incognito, login_check=True, wait_sec=10, driver_path=None):
        """
        :param wait_sec: waiting for chatgpt response time
        """ 
        ssl._create_default_https_context = ssl._create_unverified_context
        # self.chrome_driver_path = ChromeDriverManager().install()
        # self.chrome_driver_path="/Users/imanpirooz/.wdm/drivers/chromedriver/mac64/126.0.6478.61/chromedriver-mac-arm64/chromedriver"
        self.chrome_driver_path = '/root/.wdm/drivers/chromedriver/linux64/133.0.6943.53/chromedriver-linux64/chromedriver'
        # self.chrome_driver_path = driver_path if driver_path != None else ChromeDriverManager().install()
        self.wait_sec = wait_sec
        self.login_check = login_check

        self.chrome_thread = None
        self.driver = self.setup_webdriver(incognito)
        # Navigate to a site that returns your IP
        self.print_myip()
        url = "https://chat.openai.com"
        self.driver.get(url)
        self.wait_for_human_verification()

        return self.driver
        # self.wait_for_human_verification()
        # try:
        #     WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
        # except:
        #     self.driver.refresh()
        #     time.sleep(2)
    
    def print_myip(self):
        self.driver.get("http://httpbin.org/ip")

        # Retrieve the page source
        page_source = self.driver.page_source

        # Parse the JSON response to extract the IP address


        print(f"My IP address is: {page_source}")
        
    async def setup_userdata(self, db, bot_id, window_id):
        download_url = await db.get_user_data_url(bot_id=bot_id)
        filepath = download_file(download_url,window_id, USERDATA_ZIP_DOWNLOAD_DIRECTORY)
        extract_zip(filepath, window_id)
        os.remove(filepath)
        
    def setup_webdriver(self, incognito):
        driver = None
        user_agent = UserAgent()
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument('--window-size=400,300')
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument("user-data-dir=/root/Desktop/test")
        # chrome_options.add_argument('--profile-directory=/root/Desktop/test')
        chrome_options.add_argument(f'user-agent={user_agent.random}')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
        chrome_options.add_argument("--incognito")
        
        # service = Service(executable_path=self.chrome_driver_path)
        # driver = webdriver.Chrome(service=service,options=chrome_options)
        # return driver
        try:
            driver = uc.Chrome(driver_executable_path=self.chrome_driver_path, options=chrome_options)
        except TypeError:
            try:
                if (Path.cwd() / self.chrome_driver_path).exists():
                    driver = uc.Chrome(executable_path=str(Path.cwd() / self.chrome_driver_path), options=chrome_options)
            except:
                driver = uc.Chrome(executable_path=self.chrome_driver_path, options=chrome_options)
        except:
            if (Path.cwd() / self.chrome_driver_path).exists():
                driver = uc.Chrome(service=ChromeService(str(Path.cwd() / self.chrome_driver_path)), options=chrome_options)
        driver.set_window_size(1024, 768)
        return driver
    
    def create_new_chat(self):
        print("start create_new_chat")
        try:
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.grow.overflow-hidden.text-ellipsis.whitespace-nowrap.text-sm.text-token-text-primary")))
            button = self.driver.find_element(By.CSS_SELECTOR, "div.grow.overflow-hidden.text-ellipsis.whitespace-nowrap.text-sm.text-token-text-primary")
            button.click()
        except:
            return 0
        time.sleep(2)
        print("end create_new_chat")
        return True
        
    def estimate_token_usage(self, text):
        # Simple estimation: Assume each token is about 4 characters long
        estimated_tokens = len(text) / 4
        
        # Adjust for punctuation and special characters if needed
        punctuation_and_special_chars = sum(not c.isalnum() and not c.isspace() for c in text)
        
        return int(estimated_tokens + punctuation_and_special_chars)

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
        print("start send_prompt_to_chatgpt")
        time.sleep(2)
        input_box = self.driver.find_element(by=By.XPATH, value='//div[contains(@id, "prompt-textarea")]')
        raw_string = repr(prompt)
        # prompt = prompt.replace("\n","\\n").replace("\'","\\\'")
        # prompt_escaped = json.dumps(prompt).strip("\"").replace("'", "\\'").replace('"', '\\"')
        input_box.click()
        input_box.send_keys(raw_string)
        time.sleep(1)
        try:
            input_box.send_keys(Keys.ENTER)
        except:
            return False
        # try:
        #     # input_btn = self.driver.find_element(by=By.CSS_SELECTOR, value="form div+button")
        #     input_btn = input_box.find_element(By.XPATH, '../following-sibling::button')
        #     time.sleep(0.1)
        #     input_btn.click()
        # except:
        #     pass
        # time.sleep(self.wait_sec)
        time.sleep(1)
        try:
            WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[data-testid="composer-speech-button"]')))
            # WebDriverWait(self.driver, self.wait_sec).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form button>[data-state=\"closed\"]")))
            # WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.XPATH, "(//form//button[@disabled])[last()]")))

            # WebDriverWait(self.driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Start voice input"]')))
        except:
            print("cannot find end response") 
            # time.sleep(self.wait_sec)
        return True
        print("end send_prompt_to_chatgpt")
    
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
        print("start return_last_response")
        try:
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'main div[data-message-author-role="assistant"]')))
            time.sleep(2)
            response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='main div[data-message-author-role="assistant"]')
            if response_elements:
                print("end return_last_response --> successful")
                return response_elements[-1].text
            else:
                print("end return_last_response --> failed")
                return ""
        except:
            print("end return_last_response --> failed")
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
        while(True):
            try:
                time.sleep(random.randint(2, 5))
                element = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR,"div.main-content>div>div>div"))
                )
                breakpoint()
                action = ActionChains(self.driver)
                action.move_to_element(element).move_by_offset(0, 0).perform()
                time.sleep(0.2)
                action.click().perform()
            except:
                print("passed")
                break
                
        
        # OLD
        # while(True):
        #     try:
        #         try:
        #             WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
        #             print("human verification passed")
        #             return 1
        #         except:
        #             element = self.driver.find_element(By.CSS_SELECTOR,'#px-captcha')
        #             action = ActionChains(self.driver)
        #             action.click_and_hold(element)
        #             action.perform()
        #             time.sleep(10)
        #             action.release(element)
        #             action.perform()
        #             time.sleep(0.2)
        #             action.release(element)
        #     except:
        #         print("human verification faild")
        #         pass
        # OLD OLD
        
        # if not self.login_check:
        #     try:
        #         WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
        #     except:
        #         time.sleep(2)
        #     return
        # print("Please complete the login or human verification steps if required.")
        # while True:
        #     user_input = input(
        #         "Press 'y' once you've finished the login or human verification, or 'n' to review again:").lower()

        #     if user_input == 'y':
        #         print("Proceeding with the automated steps...")
        #         break
        #     elif user_input == 'n':
        #         print("Please finish the human verification. Waiting for completion...")
        #         time.sleep(5)  # You can adjust the waiting time as needed
        #     else:
        #         print("Incorrect input. Please enter 'y' or 'n'.")
        # try:
        #     WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
        # except:
        #     time.sleep(2)
        # return
        
    def show_check_verify(self):
        print(" in show_check_verify")
        try:
            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, "enforcement-containerchatgpt-freeaccount")))
            print("show_check_verify failed")
            return 1
        except:
            print("show_check_verify passed")
            
            return 0
    
    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        self.driver.close()
        print("driver.close()")
        self.driver.quit()
        print("driver.quit()")