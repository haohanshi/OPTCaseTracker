from pyquery import PyQuery as pq
import requests
import smtplib
import os
import sys
import os.path
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

STATUS_OK = 0
STATUS_ERROR = -1
FILENAME_LASTSTATUS = os.path.join(sys.path[0], "{0}.txt")
SEND_GMAIL_ADDR = 'haohanshi1997@gmail.com'
SEND_GMAIL_PWD = 'pwd'

caseNumbers = []
emailRecipients = []

def check_opt_status(casenumber):
    headers = {
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language':
        'en-US, en; q=0.8, zh-Hans-CN; q=0.5, zh-Hans; q=0.3',
        'Cache-Control': 'no-cache',
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'egov.uscis.gov',
        'Referer': 'https://egov.uscis.gov/casestatus/mycasestatus.do',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'
    }
    url = "https://egov.uscis.gov/casestatus/mycasestatus.do"
    data = {"appReceiptNum": casenumber, 'caseStatusSearchBtn': 'CHECK+STATUS'}

    res = requests.post(url, data=data, headers=headers)
    doc = pq(res.text)
    status = doc('h1').text()
    code = STATUS_OK if status else STATUS_ERROR
    details = doc('.text-center p').text()
    return (code, status, details)

def send_changed_email(casenumber, recipient, oldStatus, newStatus, details):
    msg = MIMEMultipart()
    msg['From'] = SEND_GMAIL_ADDR
    msg['To'] = recipient
    msg['Subject'] = "[OPT] Your Case Status is Changed"
    message = 'Your status of case number {0} is changed.\n\n Old status:\n {1} \n\n New status:\n {2} \n\n{3}I will notify you if your status changes.\n\nHaohan Shi'.format(casenumber,oldStatus,newStatus,details)
    msg.attach(MIMEText(message))

    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(SEND_GMAIL_ADDR, SEND_GMAIL_PWD)
    mailServer.sendmail(SEND_GMAIL_ADDR, recipient, msg.as_string())
    mailServer.close()

def send_first_email(casenumber, recipient, status, details):
    msg = MIMEMultipart()
    msg['From'] = SEND_GMAIL_ADDR
    msg['To'] = recipient
    msg['Subject'] = "[OPT] Your Case Status is Recorded"
    message = 'Your status of case number {0} is recorded on server.\n\nYour current status: \n {1}\n\n {2}\n\nI will notify you if your status changes.\n\nHaohan Shi'.format(casenumber,status,details)
    msg.attach(MIMEText(message))

    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(SEND_GMAIL_ADDR, SEND_GMAIL_PWD)
    mailServer.sendmail(SEND_GMAIL_ADDR, recipient, msg.as_string())
    mailServer.close()

def main():
    while 1:
        for i in range(len(caseNumbers)):
            caseNumber = caseNumbers[i]
            emailRecipient = emailRecipients[i]
            (code, status, details) = check_opt_status(caseNumber)
            if code == STATUS_OK:
                    status = status.strip()
                    record_filepath = FILENAME_LASTSTATUS.format(caseNumber)
                    changed = False
                    last_status = None
                    if not os.path.exists(record_filepath):
                        send_first_email(caseNumber, emailRecipient, status, details)
                        with open(record_filepath, 'w') as f:
                            f.write(status)
                            f.close()
                    else:
                        with open(record_filepath, 'r+') as f:
                            last_status = f.read().strip()
                            if status != last_status:
                                changed = True
                                f.seek(0)
                                f.truncate()
                                f.write(status)
                                f.close()
                        if changed:
                            send_changed_email(caseNumber, emailRecipient, last_status, status, details)
            sleep(3)
        sleep(3600)

main()