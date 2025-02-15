import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure FlareSolverr endpoint
FLARESOLVERR_URL = "http://localhost:8191/v1"

# Step 1: Solve Cloudflare challenge using FlareSolverr
def solve_cloudflare(url):
    payload = {
        "cmd": "request.get",
        "url": url,
        "maxTimeout": 60000  # Timeout in milliseconds
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(FLARESOLVERR_URL, json=payload, headers=headers)
    response_data = response.json()
    
    if response_data.get("status") == "ok":
        return response_data["solution"]
    else:
        raise Exception(f"Failed to solve Cloudflare challenge: {response_data.get('message')}")

# Step 2: Use Selenium with the solved cookies and headers
def use_selenium_with_solution(solution):
    # Extract cookies and headers from FlareSolverr's solution
    cookies = solution["cookies"]
    user_agent = solution["userAgent"]
    
    # Configure Selenium WebDriver with User-Agent
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    service = Service("/root/.wdm/drivers/chromedriver/linux64/133.0.6943.53/chromedriver-linux64/chromedriver")  # Replace with your ChromeDriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open the target URL and set cookies manually in Selenium
    driver.get(solution["url"])
    for cookie in cookies:
        driver.add_cookie({
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"]
        })
    
    # Reload the page after setting cookies
    driver.refresh()
    
    return driver

# Example usage:
if __name__ == "__main__":
    target_url = "https://chatgpt.com"  # Replace with your target URL
    
    # Solve Cloudflare challenge using FlareSolverr
    solution = solve_cloudflare(target_url)
    
    # Use Selenium to interact with the website after solving the challenge
    driver = use_selenium_with_solution(solution)
    
    # Perform your scraping tasks here...
    driver.save_screenshot("cloudflare-challenge.png")
    # print(driver.page_source)
    
    # Close the browser session when done
    driver.quit()
