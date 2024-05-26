#try selenium with sciensedirect:
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import openpyxl
import os
import logging
import datetime
import requests
from bs4 import BeautifulSoup

#
#
excel_file_path = fr'C:\Users\Simon\Desktop\CBG\ReadingTaskDebug.xlsx'
output_dir_path = fr'C:\Users\Simon\Desktop\CBG\PDFs'
logs_dir_path = fr'C:\Users\Simon\Desktop\CBG\LogFiles'
oxyUser = "shnooker123"
oxyPW = "Ss2161992"

proxies = None
log_file = None
isNameDotPDF = True  ##distinguish between urls .../pdf/.. (FALSE) or ....pdf (true)


def download_pdf(pdfUrl, articleName, rNum):  # returns 1 if downloaded, -1 if failed
    articleName = ''.join(char for char in articleName if char.isalpha())  # remove non-alphabetical chars
    articleName = f'{rNum}_{articleName}'
    print("\t\t" + articleName)
    os.makedirs(output_dir_path, exist_ok=True)
    # Define the path to the folder where you want to save the PDF
    folder_path = output_dir_path + '\\'

    # Combine the folder path and the filename to create the full file path
    file_path = folder_path + articleName + '.pdf'

    # Send a GET request to the URL
    # if proxies:
    #     urlResp = requests.request('GET', pdfUrl, proxies=proxies, verify=False)  # urlResponse
    # else:
    try:
        # Send a GET request to the URL with a timeout
        import random

        # A list of user-agents that you can use (you can find more online)
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
            # Add more user-agents as needed
        ]

        # Randomly select a user-agent for each request
        user_aagent = random.choice(user_agents)

        urlResp = requests.get(pdfUrl, headers={'User-Agent': user_aagent})  # timout (secs) for loading the pdfUrl
        while urlResp.status_code!=200:
            print(urlResp.status_code)
            time.sleep(1)
            user_aagent = random.choice(user_agents)

            urlResp = requests.get(pdfUrl, headers={'User-Agent': user_aagent})
        # Check if the request was successful (status code 200)
        if urlResp.status_code == 200:
            # Open the file in binary write mode and write the content
            with open(file_path, 'wb') as f:
                f.write(urlResp.content)

            # Check the file size
            file_size = os.path.getsize(file_path)
            if file_size < 100:
                print(
                    f'\n\t[X] !!!~Downloaded file on row {rNum} is too small (size: {file_size} bytes). Possible corruption.\n')
                return -1
            else:
                print(f'\t[V] PDF saved to: {file_path}')
                return 1
        else:
            print(f'\n\t[X] !!!~Failed to download PDF on row {rNum}. Status code: {urlResp.status_code}\n')
            return -1
    except requests.Timeout:
        print(f'\n\t[X] !!!~Request timed out while downloading PDF on row {rNum}.\n')
        return -1
    except requests.RequestException as e:
        print(f'\n\t[X] !!!~An error occurred while downloading PDF on row {rNum}: {e}\n')
        return -1

def handleScienceDirect(baseUrl):

    driver = webdriver.Chrome()
    driver.get(baseUrl)
    time.sleep(2) # Let the user actually see something!
    pdf_link = driver.find_element(By.CSS_SELECTOR,'a[href*="-main.pdf"]')
    realURL = pdf_link.get_attribute("href")
    print(f'RealUrl is:\n\t{realURL}')
    time.sleep(3) # Let the user actually see something!

    # Close the browser
    driver.quit()
    return realURL

def main():
    # pdfUrl = handleScienceDirect("https://www.sciencedirect.com/science/article/pii/S0925231219315279")
    pdfUrl = "https://www.sciencedirect.com/science/article/pii/S0925231219315279/pdfft?md5=b135a13c0160453d3d4f792c2f5047fc&pid=1-s2.0-S0925231219315279-main.pdf"
    pdfDownloaded = download_pdf(pdfUrl,"test123",123)
    print(f'is downloaded? {pdfDownloaded}')
if __name__ == "__main__":
    main()

