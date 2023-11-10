# CBG_PDFautomation

Before starting:
1. update the next PATH variables to match your system:
  
       excel_file_path
  
       output_dir_path
  
       logs_dir_path

2. setup rotating ip mechanism:
    1. create an account on oxylabs webUnBlocker (free 1-week trial):

   https://oxylabs.io/products/web-unblocker
   
    2. change Username and Password variables to match your subscription

       oxyUser
       oxyPW

    3. note that you are not using any VPN on your computer while running.

    for self-check to see if the unBlocker works, you can try to run the next code on your CMD terminal (the one on the OS, not on your working platform/VM):

    Execute the following curl command:

        curl --insecure --proxy unblock.oxylabs.io:60000 --proxy-user "USERNAME:PASSWORD" https://ip.oxylabs.io

   The output should be a random IP.


## TBD:
- [ V ] handling CAPTHA - rotating-ip proxy implemented
- try to implement proxy stuff on response(urlPdf) (to prevent bot-blocking on pdf openning)
- catching URL - needs to checked (need to check missed out articles)
- saving file - works fine mostly (need to check missed out articles)
- marking progress in table - yet to be done, shows row on printing
- finishing a whole run - check 
