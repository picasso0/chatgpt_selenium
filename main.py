from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import random
# Start a webdriver instance and open ChatGPT
# Set up Chrome options
chrome_options = Options()
user_agents = [
    # Add your list of user agents here
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
]
# select random user agent
user_agent = random.choice(user_agents)

# pass in selected user agent as an argument
chrome_options.add_argument(f'user-agent={user_agent}')

# Add custom header
# chrome_options.add_argument("--header=Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJwd2RfYXV0aF90aW1lIjoxNzE3NjkzODMyMDgzLCJzZXNzaW9uX2lkIjoibU9xeHFkam12cnZGLXB6dUFHU1UxWTNHdGE4bE0wdUoiLCJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiJoYXNhbm10NjVAeWFob28uY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJodHRwczovL2FwaS5vcGVuYWkuY29tL2F1dGgiOnsicG9pZCI6Im9yZy1kcnhsT3BVUUYxT2lTNldrWGJ6V1J4ZTYiLCJ1c2VyX2lkIjoidXNlci1PalR4N1pyMmNRRGZzVFFyMTAySTRkOWMifSwiaXNzIjoiaHR0cHM6Ly9hdXRoMC5vcGVuYWkuY29tLyIsInN1YiI6ImF1dGgwfDYzZGQ5MzFkMjkyMzY3NTQwMmM4MGY0NyIsImF1ZCI6WyJodHRwczovL2FwaS5vcGVuYWkuY29tL3YxIiwiaHR0cHM6Ly9vcGVuYWkub3BlbmFpLmF1dGgwYXBwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE3MTc2OTM4MzYsImV4cCI6MTcxODU1NzgzNiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCBtb2RlbC5yZWFkIG1vZGVsLnJlcXVlc3Qgb3JnYW5pemF0aW9uLnJlYWQgb3JnYW5pemF0aW9uLndyaXRlIG9mZmxpbmVfYWNjZXNzIiwiYXpwIjoiVGRKSWNiZTE2V29USHROOTVueXl3aDVFNHlPbzZJdEcifQ.NqjnXk_UwOYP7BJijawHHQqXPOF550ipICYqBTqwO87n5Ex_50C1XWM7gco97ID5UHPdpaumcbTdUrzZRegnp4YrNxAZHtlZ6CD2vAO10d2IIPg-MX-Zk7ge0dENdAIKaDU6ieF2osUijjRCfPqbzZlhJkC3032wCu7Kk_sQQ5jK_f1fJn8PhiQek85WXHFaXqCuQcdUY1fi7XeHxcPl3PnS3xj5tyHoXfqVGnh39PL-Hs3_2EYGXUUXyB-lbKzx_gABm2a8MZZTMnoRfJlC_-PMcndGY5djW0iVpOmXFZXcv4ghHSD6d1ztsfUofYOYrUNAWjKiR_qF7cKndcGw4g")
# chrome_options.add_argument('--header=Cookie: oai-dm-tgt-c-240329=2024-04-02; _cfuvid=xM2_YVhnKD1v9ius2cTEEROdyIB8jX4MB1mwD0AN1zM-1717693750363-0.0.1.1-604800000; __Host-next-auth.csrf-token=144326e18e4b49140e9d586fbb4126a06ba60beb70a2cb37ec5a2580b0d7e94c%7C395be19b0f3ec4014cd845b6be098cda13dfa53db94002ef3e780bf5d414990c; oai-did=18dea969-b13b-4333-977d-720810c71927; cf_clearance=2y5N9FDBKPXHFPG0MYReWvYM4amJiPqZcoZ0vwXhvHc-1717693756-1.0.1.1-vM.60mNCoiAufkyY1SHn.xuvm_AnfW5k4CfyBjk2qYduNlFi9DpVNBI7z9G5QnpgEiz1PSPd8RoVhAV.ftIryA; oai-hlib=true; cf_chl_rc_m=1; __cflb=0H28vzvP5FJafnkHxihKaWpb7rXp6tuGnAHbaT7rPsT; __Secure-next-auth.callback-url=https%3A%2F%2Fonramp.unified-5.api.openai.com; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..vjP9lsqVQv59aZwF.qMNK1FmyKDi6mtYj95LtzC2DkPm8TL1jVqMln5fd6tkpfDn5426rrC3xGliwZRqdHX5heRJaYZct7ZoUoj1z4Mh7y2OT1LCOaN0a82y52i83eke78rpU-FrN3rQKOj6M6aO3v53bp1cmu2DNopJ15KHRt41vhFb1VQgl9HIE7tXzu5WsYXFVUwqlrE80qOdoY-cvZdOvNaZ-mvbzznXJVRBnzAjYtjCo07zZEiHiJWwEqhR65SdRqgVl1YIGnN4nuRN_PbV7BpBQBL4X-gZDAIDc7PsnInPhS1cBWP8Vl1zE-aMV7PMvzPk18HfnHi1d4nNH7g9rHN1e8cz7yj09pxP-95PK6S7aOFdmDsTCytNroT4fc8d8xwyC8fmbpds8Y8oGE5k29MO_37kjhHOmUnyAFbE6lhr8pv_CehxFG00EXJRE07-FO-eD1gxc6JteC9NDK1eFYVtbAnBDfCuyG5cIMBh9nibx88YedyyreSZR62zGIhzJaHzkO5IUGUsUyEZF8VlJ4LFdLThRMbYmN3N0f5t8z1EIy_S69YhyDrASazGdsFmh_Emhx3gU4Y2MZ_z4aejSdnZmlarqw4AppTgPElEcSNn2MbZfr7BKCy1mRhEl4S3GrxuAiSkOCA-goDzD6hSSvpomd8g66BmQSr-spKRosccqo0LN2aoC3k_Rw_GxVLzpkdgg-vZugoRhsIOK4IbQGmSx7tDl95_bO-m--GzMQI-vIwmOSl5zCTr7hPkhIO_CEDalSjO702DkVeDuZKitq2XA4lKlNvttW3wUljzq3faCIglkJRXN88d2aUD4iwrH0a-wUndqU2vUhAhBTdS9NGPWMRhcQ7KRKJWRtfnieRBrDYg-SbrQ_GKl2cWRG3Ys2b6rzwuTFFM3RQDUwPVzNhfvuWGWBo-k-GhZ3Z1_u02bkZiDomTqeZp9qyRmsIAu6ezS3uWeKMYFBkbxEH_cZ4BtZV9FrG3z2rvVLv7ATssOqB-IjgNc_DMdXSUIrpStItMQwBJfS21DVlt3l0UEjDbzQSK2XVt2Fm4F3QROJTWMRVjPswjeuC_C8QXA25c572Oq2iFSKxHj4RQ3CrReOiN340L2vf__LHQafnFF16ZCVjHffBvEayLvDOZHfmvGlpIaDxD0svXNqEUT8Su62eZ4Xk8NG-VbKE_8qu3cPCKjnd6mjDWniQfBroumlK7X7Bl-9enNyl6GpKoHjmbRBbRd4oH4Q6gnb3nIJ2iqaWYEVjSKmjnzOq8Y-_MMW8k38lFFasJJInluh9WrxufuggeM89jcY6xlR78zNSjAeBj3ODZW1p0SSo_FcCnk3HcFL7JbwpNGV9BwrHvakPKCr2vQZPWHJkXIKVvMf8IvunMYrdNWwlAug-s-m3iJNcsVPLWsOsdaKKzyOKi9D_E-JIzZXeYGFLqkTWCprz7vvgm_x5bCAcMAD1mTnlzsdOUZuHBhN-9jIwzuQFOQe_6hQRaiPqRnZYOwBcqWdrAPidgzaBFZwZqDhfiKswcy7iXkj4_cGZYKH6bM6ZWFvAPN_58ng-EKs6cNJg6uuJTvDx6ooTxeaDEXFi7hz5HjgfNZA51wsAiSLMG-puSYaRe0deSXL5i86PLpRsqFZqZRAb9BTDDShuuMk4ED1hCmkfNyPSe6WmuMtFQRr_nM-nrIz9kirZ-byw-c5L3sxcvGPC5qFtReQ7_Mpqdz-UxhrYStma5UVkujW3FpsYgi1vRImzoi4XUnXgdcPjOIJ2MKnawUw27Oro6a3K4deH1rzM83G11zWYeMtUMUF01qzra0tBbVtoYSd9Ypjjo_Rcq17NT8Jw4tKolSCihbCtKm83jexTmKeBworW4bO8BEewZQIC2fTeAwxIzbux4pa29ekgabQnnF7Q2-SQ5p191UB7ps0okrzefwSQYbirX09n0WG2wj8vLt8yCuvufL2uTPurkVNM0J3m6QVV8EIvbqPrOjYbhnPG1E7wiKGBtfC9IbaGR6BHAxDunJlIRLsZs1Pll53P9b2wmyDBvHqWqH_DKJgTEhUW2g9N0yiVSq2g6EHewTTV3h_ZAA73VWjO0Aepz3hQyJLrieI5TioWATvN9ENQbaAAd7cZAV_QUcjOOVRiXCC6U0YUeyo3rGpjGgVCHyMV5YGANfoPB4uykmXQkyeuNoM94wmFi-nKXBWu5JBFuSDHvuNXfClPEGoZtgZitV2dJ5FllZNk_znjPMfbz9zyA-gpSz-N75prz2qmC3vJvvUudf0SHvnhH2kd9opIipq3lTbbrQwvQ5WL-nYEuwl8vBKRXkPFPVzhFcMZWZ652u_tL_GbyqLCQcFMkXkwTVzAM_POECSVA9_6-RFdMu4RXFnmJXPUjExJ_t0tA30o-maHcpw0KRt9tOwzqm9RvGDofbhjo0_dV3GPAOwNnMsqX5nz__9Ny6s5Y1d9obo9uCsvDEVjaCrkfUL3hmCQWYguoP-wkOnrw-QITyiczFWz4bymGXZbNMKpJjO28QNT3cY0-QIzxeodkfdK-xeDx4eycf9di4iC5ywM4WaPRfCExkTMrEiihZ_KPaJ0XtjRD3Epf20X02G32USuJHDk7br5BqYQqBZ8dwa55mpv4g-oKoyfIzkVo3XcAZzY9hDm2YtliPN1HuTuIz9HrrLxITVhJkhhLklWxU6CLd5MYPA498IB565JDP-6XkU0Xdrk84zhhoTQP9xls3dGp54S462wBwNTWMtzv96ubiDRHcYn7gvL71kJ-aAGN5Gaq9KuA9Xe32kynW0NrJBJiyXcjx-LRkzKPHQhX88pKMREPa3ggnpr8Gb1Mpag372lHGlon1MYlQa95MJsTQOfhRmCwpzfC0cKwO-hvnE2u0agR22AI0Z39zsE_vg3zrlfQc-UJhawFf6l6sUwJ69FqpUQ_yxgnpJAwx-9ohN8c2WaY-qeDiwvnQIWeWkW0ZBG-MeEAOxqku6ygjV4HcEmpaerhT5xoUVYnQB2Zcw1mOpoaPKxPoiSg_tARxmnMejOiFzF68GcL8WLt_ke0DrvUDIgsu3rVlMgyxHBaix2RnJ2NkYw.NOJTGOoBdhTnAhDRVuJlIw; _dd_s=rum=0&expire=1717778576932; _umsid="Z0FBQUFBQm1ZelVQWWJRUk9tUFAtSDhIeFl4anJPN284YjlRQ0pySWVONmtQMGp1bVRVZGFOMERuQ0EwdVhQWU1MN1ljYnJOT0doNEp5LUxRMjg0WXdEVHJwUVB5bnhPeGFLSlB4U1V3N0JOUVM2SHVFRzZnVzlLUWxMN0FRMnZla0FSNFZzSjNycTlybEltVUJVUVJQWHc2MllyUXNHS1JzRTZFYlhvR1Nza21jNXM1WXk4YlFVZ185VkZsMXVNYzAwYUFoT0R3eVhVcHI1TnpIY2Q1dFBQOGlnVnF2MVZualBuWENUVEd4RmNmMEJobFFDdzJQTT0="; __cf_bm=A8MuMvrpxH7S8SMAMSTZb1K3hXtJNTRZd7aCaOeRNZg-1717777679-1.0.1.1-U7wIaXk3fnsJTU46o40wZtX_0dUqY8iwgUTWFbrhIRnQrdv8KbWaVrIzb41t4WWeChy0QIrsc2lFaJ55r1HSgQ')
# chrome_options.add_argument('--header=Referer: https://chatgpt.com/')
chrome_options.add_experimental_option(
            'prefs', {'intl.accept_languages': 'en,en_US'})

chrome_options.add_argument(
            f"user-data-dir=/Users/imanpirooz/repo/chatgpt/Chrome")

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://chatgpt.com/')
sleep(5)
breakpoint()
try:
    while(True):
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe")))
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label"))).click()
        sleep(5)
except:
    pass
# Find the input field and send a question
input_field = driver.find_element_by_class_name('c-text-input')
input_field.send_keys('What is the capital of France?')
input_field.send_keys(Keys.RETURN)

# Wait for ChatGPT to respond
driver.implicitly_wait(10)

# Find the response and save it to a file
response = driver.find_element_by_class_name('c-message__body').text
with open('response.txt', 'w') as f:
    f.write(response)

# Close the webdriver instance
driver.quit()