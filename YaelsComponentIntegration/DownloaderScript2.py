import atexit
import time
import os
import logging
import datetime
import requests
import pandas as pd
import json  # Added for JSON parsing
from bs4 import BeautifulSoup

# File paths and credentials
citations_json_file_path = fr'C:\Users\Simon\PycharmProjects\CBGproject\YaelsComponentIntegration\citations.json'  # Changed to JSON file
output_dir_path = fr'C:\Users\Simon\PycharmProjects\CBGproject\YaelsComponentIntegration\PDFs'
logs_dir_path = fr'C:\Users\Simon\PycharmProjects\CBGproject\YaelsComponentIntegration\LogFiles'
oxyUser = "customer-CBG443_0TVYT"
oxyPW = "Aa1234567890"

proxies = None
log_file = None
blocked_sites = ["sciencedirect", "ieeexplore", "aiia.csd", "link.springer",
                 "onlinelibrary.wiley"]  # Add more sites as needed -  "researchgate"


def startProxy(username, password):
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    global proxies
    prxStr = f'http://{username}:{password}@pr.oxylabs.io:7777'
    proxy = prxStr
    proxies = {
        'http': proxy,
        'https': proxy
    }
    prntL(f'\tstarting proxy: {proxy}')


def getBibtex(citation):  # Modified to use citation from JSON
    bibtex = citation['bibtex']
    if bibtex is None:
        bibtex = citation['title']
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
        return True
    return False


def find_pdf_links(bibtex):  # bibtex > pdfUrl
    page = f'https://scholar.google.com/scholar?q={bibtex}'
    if proxies:
        response = requests.request('GET', page, verify=False, proxies=proxies)
        if checkResponseStatus(response):
            prntL("second try after RECAPTCHA (bad proxy):")
            response = requests.request('GET', page, verify=False, proxies=proxies)
    else:
        response = requests.get(page)
        checkResponseStatus(response)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        selectors = ['a[href$=".pdf"]', 'a[href*="/pdf"]', 'a[href*="/article/"]', 'a[href*="/download"]',
                     'a[href*="/document/"]', 'a[href*="servlets/purl/"]', 'a[href*="doi/abs/"]']
        for selector in selectors:
            pdf_links = soup.select(selector)
            if pdf_links:
                return pdf_links

        prntL("Could not find PDF URLs")
        return []


def markAsDownloaded(citations, key):  # Modified to update JSON
    citations[key]['isDownloaded'] = True
    with open(citations_json_file_path, 'w', encoding='utf-8') as file:  # Write back to JSON
        json.dump(citations, file, indent=4)
    prntL(f"Updated 'isDownloaded' for item {key}")


def twistBlockedUrl(pdfUrl):
    newUrl = 'https://sci-hub.se/'
    if "ieeexplore" in pdfUrl.lower():
        if "abstract/document/" in pdfUrl.lower():
            newUrl = newUrl + pdfUrl
            print(f'\tnew URL is: {newUrl}')
            return newUrl
        base_name = os.path.splitext(os.path.basename(pdfUrl))[0]
        desired_part_with_zeros = base_name.split('/')[-1]
        desired_part_without_zeros = str(int(desired_part_with_zeros))
        newUrl = 'https://sci-hub.se/https://ieeexplore.ieee.org/document/' + desired_part_without_zeros
    if "sciencedirect" in pdfUrl.lower() and "/am/" in pdfUrl.lower():
        pdfUrl = pdfUrl.replace("/am/", "/")
        newUrl = newUrl + pdfUrl
    else:
        newUrl = newUrl + pdfUrl
    print(f'\tnew URL is: {newUrl}')
    return newUrl


def download_pdf(pdfUrl, articleName, rNum):
    if articleName == None:
        articleName = f"NoArticleTitle_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    else:
        articleName = ''.join(char for char in articleName if char.isalpha())
    articleName = f'{rNum}_{articleName}'
    prntL("\t\t" + articleName)
    os.makedirs(output_dir_path, exist_ok=True)
    folder_path = output_dir_path + '\\'
    file_path = folder_path + articleName + '.pdf'
    tryWithSciHub = False
    try:
        if any(site in pdfUrl.lower() for site in blocked_sites):
            tryWithSciHub = True
            pdfUrl = twistBlockedUrl(pdfUrl)
            prntL("@@@@running a try with SciHub")
        urlResp = requests.get(pdfUrl, timeout=4)

        if urlResp.status_code == 200:
            if tryWithSciHub:
                soup = BeautifulSoup(urlResp.content, 'html.parser')

                if "Unfortunately, Sci-Hub" in urlResp.text:
                    prntL(f'\n\t[X] !!!~An error occurred while downloading PDF on row {rNum}:\n'
                          f'\t\tthe link is not available on sci-hub')
                    return -1

                embed_tag = soup.find('div', id='article').find('embed')
                pdf_url_relative = embed_tag['src']
                base_url = 'https://sci-hub.se/'
                pdf_url = base_url + pdf_url_relative
                pdf_resp = requests.get(pdf_url, timeout=10)
                if pdf_resp.status_code == 200:
                    urlResp = pdf_resp
                else:
                    prntL(f'\n\t[X] !!!~An error occurred while downloading PDF on row {rNum}:\n'
                          f'the pdfResp status code (from SciHub) is: {pdf_resp.status_code}')
                    return -1

            with open(file_path, 'wb') as f:
                f.write(urlResp.content)

            file_size = os.path.getsize(file_path)
            if file_size < 100:
                prntL(
                    f'\n\t[X] ~ Downloaded file on row {rNum} is too small (size: {file_size} bytes). Possible corruption.\n')
                return -1
            else:
                prntL(f'\t[V] PDF saved to: {file_path}')
                return 1
        else:
            prntL(
                f'\n\t[X] !!!~Failed to download PDF on row {rNum}. Status code: {urlResp.status_code}. For further examination check the log.\n')
            logging.info(urlResp.text)
            return -1
    except requests.Timeout:
        prntL(f'\n\t[X] !!!~Request timed out while downloading PDF on row {rNum}.\n')
        return -1
    except requests.RequestException as e:
        prntL(f'\n\t[X] !!!~An error occurred while downloading PDF on row {rNum}: {e}\n')
        return -1


def setup_logging():
    global log_file
    os.makedirs(logs_dir_path, exist_ok=True)

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


def cleanup():
    prntL("~~atExit: in cleanup")
    prntL("~~atExit: WorkBook closed")
    close_logging()


atexit.register(cleanup)


def main():
    try:
        setup_logging()
        # startProxy(oxyUser, oxyPW)
        prntL(f'starting, running on this input file:\n {citations_json_file_path}')  # Changed to JSON file path

        with open(citations_json_file_path, 'r', encoding='utf-8') as file:  # Specify encoding
            citations = json.load(file)

        for key, citation in citations.items():  # Iterate through JSON citations
            if citation.get('isDownloaded', False):  # Skip if already downloaded
                prntL(f"Skipping already downloaded item {key}")
                continue

            rowNum = int(key)
            title = citation['title']
            bibtex = getBibtex(citation)
            pdf_links = find_pdf_links(bibtex)
            if not pdf_links:
                prntL("@@@second try - search scholar by title not bibtex")
                pdf_links = find_pdf_links(title)
            firstTimeOnly = True
            for pdf_link in pdf_links:
                if firstTimeOnly:
                    pdf_url = pdf_link['href']
                    prntL(pdf_url)
                    try:
                        if download_pdf(pdf_url, title, rowNum) == 1:
                            logging.info(f'successful downloading')
                            markAsDownloaded(citations, key)  # Update JSON
                        else:
                            logging.info(f'download failed')
                    except Exception as e:
                        logging.error(f'Exception while processing PDF on row {rowNum}: {e}')
                    finally:
                        firstTimeOnly = False
                else:
                    pdf_url = pdf_link['href']
                    prntL(f'another URL found:  {pdf_url}')
            time.sleep(1)
        prntL(f'~~FINISHED RUNNING {"with" if proxies else "WITHOUT"} proxies')
    except KeyboardInterrupt:
        prntL("Script execution manually interrupted.")
    except Exception as e:
        prntL(f'An unexpected exception occurred:\n\t {e}')


if __name__ == "__main__":
    main()
