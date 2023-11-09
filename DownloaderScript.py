import time
import openpyxl
import os
import logging
import datetime
import requests
from bs4 import BeautifulSoup


isNameDotPDF = True  ##distinguish between urls .../pdf/.. (FALSE) or ....pdf (true)
# oxyUser = "USERNAME"
# oxyPW = "PASSWORD"
# prxStr = f'http://{oxyUser}:{oxyPW}@unblock.oxylabs.io:60000'
# proxy = prxStr
# proxies = {
#     'http': proxy,
#     'https': proxy
# }
#
#
excel_file_path = fr'C:\Users\Simon\Desktop\CBG\ReadingTaskAll.xlsx'
output_dir_path = fr'C:\Users\Simon\Desktop\CBG\PDFs'
logs_dir_path = fr'C:\Users\Simon\Desktop\CBG\LogFiles'
log_file = None


def getBibtex(row, rowNum):  # rowNum > bibtex
    prntL(f"row num: {rowNum} [by {row[0]} {row[1]}, article name: {row[4]} ~ {row[7]}] ")
    bibtex = row[10]
    return bibtex


def checkResponseStatus(response):
    prntL(f'response code is: {response.status_code}')
    if response.status_code == 403:
        prntL("Bot blocked (403 Forbidden)")
    if "CAPTCHA" in response.text:
        prntL("CAPTCHA encountered in response content")
    if "x-captcha" in response.headers or "x-bot-detection" in response.headers:
        prntL("Bot blocking detected in response headers")
    if "Retry-After" in response.headers or "Rate-Limit" in response.headers:
        prntL("Rate limiting detected")
    if "captcha" in response.text.lower():
        prntL("\t!!! You are facing RECAPTCHA !!!")


def find_pdf_links(bibtex):  # bibtex > pdfUrl
    # Make a request to Google Scholar with the 'bibtex' variable
    page = f'https://scholar.google.com/scholar?q={bibtex}'
    response = requests.get(page)  # , proxies=proxies, verify=False)
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


def download_pdf(pdfUrl, articleName):
    articleName = articleName.replace(':', '_')
    os.makedirs(output_dir_path, exist_ok=True)
    # Define the path to the folder where you want to save the PDF
    folder_path = output_dir_path + '\\'

    # Combine the folder path and the filename to create the full file path
    file_path = folder_path + articleName + '.pdf'

    # Send a GET request to the URL
    urlResp = requests.get(pdfUrl)

    # Check if the request was successful (status code 200)
    if urlResp.status_code == 200:
        # Open the file in binary write mode and write the content
        with open(file_path, 'wb') as f:
            f.write(urlResp.content)
        prntL(f'PDF saved to: {file_path}')
    else:
        prntL(f'Failed to download PDF. Status code: {urlResp.status_code}')


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


#
# # ~~~~~~~~~~~~~Start OF LOG STUFF~~~~~~~~~~~~~~~~~~~~~
# class PrintToLogHandler(logging.Handler):
#     def emit(self, record):
#         log_entry = self.format(record)
#         print(log_entry)
#         with open(os.path.join(self.log_dir, self.log_file), 'a') as log_file:
#             log_file.write(log_entry + '\n')
#
#
# def setup_logging(log_dir):
#     os.makedirs(log_dir, exist_ok=True)
#     log_str = f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
#     log_file = os.path.join(log_dir, log_str)
#
#     logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s [%(levelname)s] - %(message)s')
#
#     print_to_log_handler = PrintToLogHandler()
#     print_to_log_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s'))
#     print_to_log_handler.setLevel(logging.INFO)
#     print_to_log_handler.log_dir = log_dir  # Assign the log directory to the handler
#     print_to_log_handler.log_file = log_str  # Assign the log file name to the handler
#
#     root_logger = logging.getLogger()
#     root_logger.addHandler(print_to_log_handler)
#
#
# def close_logging():
#     root_logger = logging.getLogger()
#     for handler in root_logger.handlers[:]:
#         root_logger.removeHandler(handler)
#         handler.close()
#

def prntL(someString):
    logging.info(someString)
    print(someString)


# ~~~~~~~~~~~~~END OF LOG STUFF~~~~~~~~~~~~~~~~~~~~~


def main():
    setup_logging()
    prntL("starting")
    wb = openpyxl.load_workbook(excel_file_path)
    sheet = wb.active
    rowNum = 1
    for row in sheet.iter_rows(min_row=2, values_only=True):
        # global rowNum
        rowNum += 1
        bibtex = getBibtex(row, rowNum)
        pdf_links, isNameDotPDF = find_pdf_links(bibtex)  ##method updates both variables
        for pdf_link in pdf_links:
            pdf_url = pdf_link['href']
            prntL(pdf_url)
            download_pdf(pdf_url, row[7])
        time.sleep(1)

    #     ~~finishings:~~
    close_logging()
    wb.close()


if __name__ == "__main__":
    main()
