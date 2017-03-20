from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import calendar
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from collections import OrderedDict
import sys

website = 'http://www.yellowstonenationalparklodges.com'


def check_hotel(hotels, dates, month=8, year='2017', adults=2):
    hotel_available = OrderedDict()
    driver = webdriver.Firefox(executable_path=r'/Users/shawn/Documents/geckodriver')
    driver.get(website)

    arrival = year + '-' + str(format(month, '02')) + '-' + str(format(dates[0], '02'))
    departure = year + '-' + str(format(month, '02')) + '-' + str(format(dates[0] + 1, '02'))

    for hotel in hotels:
        driver.switch_to.window(driver.window_handles[0])
        Select(driver.find_element_by_xpath("//select[@id='sn-location']")).select_by_visible_text(hotel)
        Select(driver.find_element_by_xpath("//select[@id='adults']")).select_by_visible_text(str(adults))
        elem = driver.find_element_by_id('sn-arrival')
        elem.clear()
        elem.send_keys(arrival)
        elem = driver.find_element_by_id('sn-departure')
        elem.clear()
        elem.send_keys(departure)
        driver.find_element_by_css_selector("div.booking:nth-child(5) > div:nth-child(1) > \
                                            form:nth-child(1) > div:nth-child(11) > input:nth-child(2)").click()

        driver.switch_to.window(driver.window_handles[1])

        for date in dates:
            arrival = year + '-' + str(format(month, '02')) + '-' + str(format(date, '02'))
            try:
                WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "PWK_NUM")))
                Select(driver.find_element_by_xpath("//select[@name='LRESYRMTH']")).select_by_visible_text(
                    str(year) + " " + calendar.month_name[month])
                Select(driver.find_element_by_xpath("//select[@name='LRESDDX']")).select_by_index(date - 1)

                select = Select(driver.find_element_by_id("PWK_NUM"))
                room_type_num = len(select.options)

                driver.find_element_by_css_selector(
                    "div.col-xs-12:nth-child(8) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > a:nth-child(1)").click()

                time.sleep(2)
                WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, "rmlist" + str(room_type_num))))
                for i in xrange(1, room_type_num + 1):
                    price = driver.find_element_by_css_selector("#rmlist" + str(
                        i) + " > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > h3").text.encode(
                        "ascii")
                    if price:
                        hotel_name_and_date = driver.find_element_by_css_selector("#rmlist" + str(
                            i) + " > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)").text.encode(
                            "ascii")
                        hotel_info = hotel_name_and_date.replace('\n\n', '\n').split('\n')
                        key = hotel_info[1] + " - " + hotel_info[2]
                        name = hotel_info[0]
                        if key not in hotel_available:
                            hotel_available[key] = ["{0} : {1}\n".format(name, price)]
                        else:
                            hotel_available[key].append("{0} : {1}\n".format(name, price))
            except Exception as e:
                print e
                pass
            finally:
                pass
        driver.close()

    driver.quit()
    return hotel_available


def process_text_body(hotel_list):
    text = ""
    for (date, hotel) in hotel_list.items():
        text += "\n\n\n=========== " + date + " ===========\n\n"
        for opt in hotel:
            text += opt
    text += '\n\nbook here:' + website
    return text


def send_email(user, pwd, recipients, text_body):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Link"
    msg['From'] = user
    msg['To'] = ';'.join(recipients)

    msg.attach(MIMEText(text_body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(user, pwd)

    server.sendmail(user, recipients, msg.as_string())
    server.quit()


def main(argv):

    if len(argv) < 2:
        email = False
        print "please provide Gmail accounts and password if you want to receive notification via email"
        print "i.e. yellowstone.py user1_account@gmail.com user1_password user2@gmail.com"
    else:
        email = True
        num = len(argv)
        recipients = [argv[0]] + argv[2:num]

    hotels = [
        'Canyon Lodge',
        'Grant Village',
        'Lake Hotel and Cabins',
        'Lake Lodge',
        'Mammoth Hotel and Cabins',
        'Old Faithful Inn',
        'Old Faithful Lodge',
        'Old Faithful Snow Lodge',
        'Roosevelt Lodge',
    ]

    dates = [9, 10, 11, 12, 13]
    month = 8
    hotel_available = check_hotel(hotels, dates, month=month)

    result = process_text_body(hotel_available)
    if email:
        send_email(argv[0], argv[1], recipients, result)
    else:
        print result


if __name__ == '__main__':
    main(sys.argv[1:])
