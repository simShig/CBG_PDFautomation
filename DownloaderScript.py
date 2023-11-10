import time
import openpyxl
import os
import logging
import datetime
import requests
from bs4 import BeautifulSoup

#
#
excel_file_path = fr'C:\Users\Simon\Desktop\CBG\ReadingTaskAll.xlsx'
output_dir_path = fr'C:\Users\Simon\Desktop\CBG\PDFs'
logs_dir_path = fr'C:\Users\Simon\Desktop\CBG\LogFiles'
oxyUser = "shnooker123"
oxyPW = "Ss2161992"

proxies = None
log_file = None
isNameDotPDF = True  ##distinguish between urls .../pdf/.. (FALSE) or ....pdf (true)


def startProxy(username, password):
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    global proxies
    prxStr = f'http://{username}:{password}@unblock.oxylabs.io:60000'
    proxy = prxStr
    proxies = {
        'http': proxy,
        'https': proxy
    }
    prntL(f'\tstarting proxy: {proxy}')


def getBibtex(row, rowNum):  # rowNum > bibtex
    prntL(f"row num: {rowNum} [by {row[0]} {row[1]}, article name: {row[4]} ~ {row[7]}] ")
    bibtex = row[10]
    return bibtex


def checkResponseStatus(response):
    logging.info(f'response code is: {response.status_code}')
    if response.status_code == 403:
        prntL("Bot blocked (403 Forbidden)")
    if response.status_code == 418:
        prntL("418 teapot <=> Bot blocked (like 403 Forbidden)")
    if response.status_code == 550:
        prntL("The recipient is blocking your email on the recipient's email server (550 Forbidden)")
    if "captcha" in response.text.lower():
        prntL("\t!!! You are facing RECAPTCHA !!!")


def find_pdf_links(bibtex):  # bibtex > pdfUrl
    # Make a request to Google Scholar with the 'bibtex' variable
    page = f'https://scholar.google.com/scholar?q={bibtex}'
    if proxies:
        response = requests.request('GET', page, verify=False, proxies=proxies)  # , proxies=proxies, verify=False)
    else:
        response = requests.get(page)
    checkResponseStatus(response)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        selectors = ['a[href$=".pdf"]', 'a[href*="/pdf"]', 'a[href*="/article/"]', 'a[href*="/download"]']
        for selector in selectors:
            pdf_links = soup.select(selector)
            if pdf_links:
                isNameDotPDF = selector in ('a[href$=".pdf"]',)
                return pdf_links, isNameDotPDF

        prntL("Could not find PDF URLs")
        # prntL(response.text)
        # logging.info("Could not find PDF URLs")
        return [], False


def download_pdf(pdfUrl, articleName, rNum):
    articleName = ''.join(char for char in articleName if char.isalpha())       ##remove non-alphabetical chars
    articleName=f'{rNum}_{articleName}'
    print("\t\t"+articleName)
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
        urlResp = requests.get(pdfUrl, timeout=4)  # timout (secs) for loading the pdfUrl

        # Check if the request was successful (status code 200)
        if urlResp.status_code == 200:
            # Open the file in binary write mode and write the content
            with open(file_path, 'wb') as f:
                f.write(urlResp.content)
            prntL(f'\t[V] PDF saved to: {file_path}')
        else:
            prntL(f'\n\t[X] !!!~Failed to download PDF on row {rNum}. Status code: {urlResp.status_code}\n')
    except requests.Timeout:
        prntL(f'\n\t[X] !!!~Request timed out while downloading PDF on row {rNum}.\n')
    except requests.RequestException as e:
        prntL(f'\n\t[X] !!!~An error occurred while downloading PDF on row {rNum}: {e}\n')

def setup_logging():
    global log_file
    os.makedirs(logs_dir_path, exist_ok=True)

    # Generate a unique log file name with a timestamp
    log_str = f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_file = os.path.join(logs_dir_path + '\\', log_str)
    print(log_file)
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')



def close_logging():
    global log_file
    if log_file is not None:
        log_file_handler = None
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.FileHandler):
                log_file_handler = handler
                break

        if log_file_handler is not None:
            log_file_handler.stream.close()
            logging.getLogger().removeHandler(log_file_handler)
        log_file = None


def prntL(someString):
    logging.info(someString)
    print(someString)


def main():
    setup_logging()
    startProxy(oxyUser, oxyPW)
    prntL("starting")
    wb = openpyxl.load_workbook(excel_file_path)
    sheet = wb.active
    rowNum = 1
    for row in sheet.iter_rows(min_row=2, values_only=True):
        # global rowNum
        rowNum += 1
        bibtex = getBibtex(row, rowNum)
        pdf_links, isNameDotPDF = find_pdf_links(bibtex)  ##method updates both variables
        firstTimeOnly = True
        for pdf_link in pdf_links:
            if firstTimeOnly:
                pdf_url = pdf_link['href']
                prntL(pdf_url)
                download_pdf(pdf_url, row[7], rowNum)
                firstTimeOnly = False
            else:
                pdf_url = pdf_link['href']
                prntL(f'another URL found:  {pdf_url}')
        time.sleep(1)

    #     ~~finishings:~~
    close_logging()
    wb.close()


if __name__ == "__main__":
    main()


