# from selenium import webdriver
#
# driver = webdriver.Firefox()
# driver.get("https://www.sciencedirect.com/science/article/pii/S2214212618305866/pdf")
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
# from webdriver_manager.firefox import GeckoDriverManager
# #
# # driver = webdriver.Firefox(
# #
# #     executable_path=GeckoDriverManager().install())
# # driver.close()
# 
# # Set up Firefox options
# firefox_options = Options()
# # Set the download directory
# firefox_options.set_preference("browser.download.folderList", 2)
# firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
# firefox_options.set_preference("browser.download.dir", fr'C:\Users\Simon\Desktop\CBG\PDFs')
# firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
# 
# # Create a Firefox driver with the specified options
# driver = webdriver.Firefox(options=firefox_options)
# 
# # Replace 'your_pdf_url' with the actual URL of the PDF you want to open
# base_url = 'https://sci-hub.se/https://www.sciencedirect.com/science/article/pii/S2214212618305866'
# driver.get(base_url)
# 
# # Wait for the PDF button to be present in the DOM
# pdf_button = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.CSS_SELECTOR, 'a.link-button'))
# )
# 
# pdf_button.click()
# time.sleep(5)
# # # Wait for the PDF to load (you might need to adjust the timeout)
# # wait = WebDriverWait(driver, 10)
# # wait.until(EC.presence_of_element_located((By.TAG_NAME, 'embed')))
# 
# # Optionally, you can add further logic to interact with the PDF page if needed
# 
# # Close the browser (optional)
# driver.quit()
import atexit
import time
import openpyxl
import os
import logging
import datetime
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup  # You need to install the BeautifulSoup library

#
#
excel_file_path = fr'C:\Users\Simon\Desktop\CBG\ReadingTaskDebug.xlsx'
output_dir_path = fr'C:\Users\Simon\Desktop\CBG\PDFs'
logs_dir_path = fr'C:\Users\Simon\Desktop\CBG\LogFiles'

blocked_sites = ["sciencedirect","ieeexplore", "aiia.csd"]  # Add more sites as needed

#
def twistBlockedUrl(pdfUrl):        ##add special twists if encounter mor problematiqe domains.
    newUrl = 'https://sci-hub.se/'
    if "ieeexplore" in pdfUrl.lower():
        base_name = os.path.splitext(os.path.basename(pdfUrl))[0]
        # Extract the desired part from the base name
        desired_part_with_zeros = base_name.split('/')[-1]
        # Remove leading zeros
        desired_part_without_zeros = str(int(desired_part_with_zeros))
        newUrl = 'https://sci-hub.se/https://ieeexplore.ieee.org/document/'+desired_part_without_zeros  #apply changes for IEEExplore
    else:
        newUrl = newUrl+pdfUrl
    print(f'\tnew URL is: {newUrl}')
    return newUrl


def download_pdf(pdfUrl, articleName, rNum):  # returns 1 if downloaded, -1 if failed
    articleName = ''.join(char for char in articleName if char.isalpha())  # remove non-alphabetical chars
    articleName = f'{rNum}_{articleName}'
    print("\t\t" + articleName)
    os.makedirs(output_dir_path, exist_ok=True)
    if any(site in pdfUrl.lower() for site in blocked_sites):
        tryWithSciHub = True
        pdfUrl = twistBlockedUrl(pdfUrl)
    try:
        # Send a GET request to the URL with a timeout
        urlResp = requests.get(pdfUrl, timeout=4)
        print(f'response status code is: {urlResp.status_code}\n'
              f'text is:\n\t{urlResp.text}')

        # Check if the request was successful (status code 200)
        if urlResp.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(urlResp.content, 'html.parser')

            if "Unfortunately, Sci-Hub" in urlResp.text:
                print(f'\n\t[X] !!!~An error occurred while downloading PDF on row {rNum}:\n'
                      f'the link is not available on sci-hub')
                return -1

            # Find the <embed> tag within the <div id="article"> section
            embed_tag = soup.find('div', id='article').find('embed')

            # Extract the PDF URL from the src attribute of the <embed> tag
            pdf_url_relative = embed_tag['src']

            # Create the absolute PDF URL by concatenating with the base URL
            base_url = 'https://sci-hub.se/'
            pdf_url = base_url + pdf_url_relative

            # Download the PDF using the extracted URL
            pdf_resp = requests.get(pdf_url, timeout=10)

            # Check if the PDF download was successful
            if pdf_resp.status_code == 200:
                # Define the path to save the PDF
                file_path = os.path.join(output_dir_path, f'{articleName}.pdf')

                # Open the file in binary write mode and write the content
                with open(file_path, 'wb') as f:
                    f.write(pdf_resp.content)

                # Check the file size
                file_size = os.path.getsize(file_path)
                if file_size < 100:
                    print(f'\n\t[X] !!!~Downloaded file on row {rNum} is too small (size: {file_size} bytes). Possible corruption.\n')
                    return -1
                else:
                    print(f'\t[V] PDF saved to: {file_path}')
                    return 1
            else:
                print(f'\n\t[X] !!!~Failed to download PDF on row {rNum}. Status code: {pdf_resp.status_code}\n')
                return -1
        else:
            print(f'\n\t[X] !!!~Failed to download PDF on row {rNum}. Status code: {urlResp.status_code}\n')
            return -1
    except requests.Timeout:
        print(f'\n\t[X] !!!~Request timed out while downloading PDF on row {rNum}.\n')
        return -1
    except requests.RequestException as e:
        print(f'\n\t[X] !!!~An error occurred while downloading PDF on row {rNum}: {e}\n')
        return -1










def main():
    articleName = "An Ensemble Deep Learning-Based Cyber-Attack Detection in Industrial Control System"
    baseURL = 'https://ieeexplore.ieee.org/'
    userName = 'shnooker123@gmail.com'
    userPW = '123qweasd'
    pdfUrl = 'https://ieeexplore.ieee.org/iel7/6287639/8600701/08727539'
    print(download_pdf(pdfUrl,"sdfds",2))

if __name__ == "__main__":
    main()
