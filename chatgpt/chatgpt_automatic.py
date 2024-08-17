from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from pathlib import Path
import time
import os
import ssl
import json
from io import StringIO
from utils import download_file, extract_zip
from global_vars import USERDATA_ZIP_DOWNLOAD_DIRECTORY

class ChatGPTAutomator:
    def __init__(self):
        pass
    async def initialize(self, db, window_id, bot_id, login_check=True, wait_sec=10, driver_path=None):
        """
        :param wait_sec: waiting for chatgpt response time
        """ 
        ssl._create_default_https_context = ssl._create_unverified_context
        self.window_id = window_id
        # self.chrome_driver_path = ChromeDriverManager().install()
        # self.chrome_driver_path="/Users/imanpirooz/.wdm/drivers/chromedriver/mac64/126.0.6478.61/chromedriver-mac-arm64/chromedriver"
        self.chrome_driver_path = '/home/rdp/.wdm/drivers/chromedriver/linux64/127.0.6533.119/chromedriver-linux64/chromedriver'
        # self.chrome_driver_path = driver_path if driver_path != None else ChromeDriverManager().install()
        self.wait_sec = wait_sec
        self.login_check = login_check

        self.chrome_thread = None
        await self.setup_userdata(db=db, bot_id=bot_id, window_id=window_id)
        # copytree('gpt3_userdata',window_id)
        self.driver = self.setup_webdriver()
        url = "https://chat.openai.com"
        self.driver.get(url)
        # self.wait_for_human_verification()
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
        except:
            self.driver.refresh()
            time.sleep(2)

    async def setup_userdata(self, db, bot_id, window_id):
        download_url = await db.get_user_data_url(bot_id=bot_id)
        filepath = download_file(download_url,window_id, USERDATA_ZIP_DOWNLOAD_DIRECTORY)
        extract_zip(filepath, window_id)
        os.remove(filepath)
        
    def setup_webdriver(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--window-size=400,300')
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f"--user-data-dir={self.window_id}/remote-profile");
        try:
            driver = uc.Chrome(driver_executable_path=self.chrome_driver_path,user_data_dir=f"{self.window_id}/remote-profile", options=chrome_options)
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
        try:
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.grow.overflow-hidden.text-ellipsis.whitespace-nowrap.text-sm.text-token-text-primary")))
            button = self.driver.find_element(By.CSS_SELECTOR, "div.grow.overflow-hidden.text-ellipsis.whitespace-nowrap.text-sm.text-token-text-primary")
            button.click()
        except:
            pass
    
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
        time.sleep(1)
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
            time.sleep(2)
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
        while(True):
            try:
                try:
                    WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form textarea")))
                    print("human verification passed")
                    return 1
                except:
                    element = self.driver.find_element_by_css_selector('#px-captcha')
                    action = ActionChains(self.driver)
                    action.click_and_hold(element)
                    action.perform()
                    time.sleep(10)
                    action.release(element)
                    action.perform()
                    time.sleep(0.2)
                    action.release(element)
            except:
                print("human verification faild")
                pass
        # OLD
        
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
    
    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        self.driver.close()
        print("driver.close()")
        self.driver.quit()
        print("driver.quit()")
