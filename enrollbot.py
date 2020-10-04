from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import randint

import time 
import datetime
import schedule
import sched
import sys

username = "put your username here"
password = "put your password here"
# ex: "10:30" uses 24 hour format
# use leading zeroes for hours less than 10, i.e. 09:00
target_time = "string of the time you want the program to start"
target_time = "01:57"

def get_element(web_driver, xpath, timeout=5):

    element = None
    try:
        element = WebDriverWait(web_driver, timeout).until(
            EC.presence_of_element_located( (By.XPATH, xpath) )
        )
    except:
        print("failed to find element with xpath: ", xpath)

    return element

def is_button_clickable(button_element):
    return button_element.is_displayed() and button_element.is_enabled()


def enroll():

    # instance of Firefox is created
    driver = webdriver.Firefox()
    # navigates to page given URL
    login_url = "https://cas.ucalgary.ca/cas/login?service=https://portal.my.ucalgary.ca/psp/paprd/?cmd=start&ca.ucalgary.authent.ucid=true" 
    driver.get(login_url)
    # confirms that title has 'Python' in it
    #assert "Python" in driver.title
    # q is the input text element
    username_box = driver.find_element_by_id("eidtext")
    # set username
    username_box.clear()
    username_box.send_keys(username)
    password_box = driver.find_element_by_id("passwordtext")
    # set password
    password_box.send_keys(password)
    password_box.send_keys(Keys.RETURN)
    #print(driver.page_source)

    # wait up to 15 seconds for next page
    WebDriverWait(driver, 15).until(EC.url_changes(login_url))
    new_url = "https://portal.my.ucalgary.ca/psp/paprd/EMPLOYEE/EMPL/h/?tab=IS_SSS_TAB&jsconfig=IS_ED_SSS_SUMMARYLnk"

    target_time_hr = int(target_time.split(":")[0])
    target_time_min = int(target_time.split(":")[1])
    first_sem_success = False
    sleep_time_bound = 1
    tries = 1

    fall_2020_button_xpath = r'//*[@id="IS_SSS_ShCtTm2207UGRDLnk"]'
    winter_2021_button_xpath = r'//*[@id="IS_SSS_ShCtTm2211UGRDLnk"]'
    spring_2020_button_xpath = r'//*[@id="IS_SSS_ShCtTm2203UGRDLnk"]'

    while (True):
        now = datetime.datetime.now()
        if (now.hour > target_time_hr or (now.minute-target_time_min) >= 5):
            print("enroll bot has tried for 5 minutes and failed, shutting down...")
            break

        print("Starting trial #", tries)
        tries += 1
        #print("new url: ", new_url)
        #time.sleep(5)
        driver.get(new_url)
        # click on course search
        #course_search_button_class = ".ucSSS_ShCtVSBbtn.ucSSS_BtnPopUpIcon"
        #course_search_button_class_xpath = "/html/body/div[3]/div[1]/ul/li/div[2]/div/div/div[2]/span/span/div/div/div[8]/div[1]/button[2]"
        #print(driver.page_source)

        curr_sem_xpath = ''
        if (not first_sem_success):
            curr_sem_xpath = fall_2020_button_xpath
        else:
            curr_sem_xpath = winter_2021_button_xpath


        # open semester tab
        sem_element = get_element(driver, curr_sem_xpath, 5)
        if (is_button_clickable(sem_element)):
            sem_element.click()
        else:
            print("failed to click semester tab, closing program")
            break

        # click add/enroll button
        add_course_button_xpath = ""
        if (curr_sem_xpath == spring_2020_button_xpath):
            add_course_button_xpath = r'/html/body/div[3]/div[1]/ul/li/div[2]/div/div/div[2]/span/span/div/div/div[8]/div[2]/button[3]'
        elif (curr_sem_xpath == fall_2020_button_xpath):
            add_course_button_xpath = r'/html/body/div[3]/div[1]/ul/li/div[2]/div/div/div[2]/span/span/div/div/div[8]/div[4]/button[3]'
        elif (curr_sem_xpath == winter_2021_button_xpath):
            add_course_button_xpath = r'/html/body/div[3]/div[1]/ul/li/div[2]/div/div/div[2]/span/span/div/div/div[8]/div[5]/button[3]'
        else:
            print("unknown semester stopping program")
            break

        element = None
        try:
            element = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable( (By.XPATH, add_course_button_xpath) )
            )
            element.click()
        except:
            print("Unable to find course search button, closing application")
            
        #time.sleep(5)
        #print(element.get_attribute("outerHTML"))
        # wait up to 15 seconds for next page
        #WebDriverWait(driver, 15).until(EC.url_changes(new_url))

        # switch to iframe of add course
        iframe_xpath = "//iframe[@name='lbFrameContent']"

        add_course_iframe = driver.find_element_by_xpath(iframe_xpath)
        driver.switch_to.frame(add_course_iframe)
        #driver.implicitly_wait(1)
        #time.sleep(2)
        # retrieve courselist table
        course_table_xpath = r'/html/body/div[1]/div/div/span/span/div/form/div[5]/table/tbody/tr/td/div/table/tbody/tr[10]/td[2]/div/table/tbody/tr/td/table/tbody/tr[4]/td[2]/div/table/tbody/tr[2]/td/table/tbody/tr[3]/td[3]/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr[2]/td/table/tbody'

        #print(driver.page_source)
        # retrieve table body
        #sleep(5)

        element = None
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located( (By.XPATH, course_table_xpath) )
            )
        except:
            print("failed to retrieve course table")

        #print(driver.page_source)
        course_checklist_table = element
        #print("table: ", course_checklist_table)
        # retrieve table elements
        table_entries = course_checklist_table.find_elements_by_tag_name("tr")
        #print("table entries: ", table_entries)
        # recursively check each row if a button can be clicked
        for entry in table_entries:

            first_layer = entry.find_elements_by_tag_name("td")
            if (len(first_layer) == 0):
                continue


            second_layer = first_layer[0].find_elements_by_tag_name("div")
            if (len(second_layer) == 0):
                continue

            button_layer = second_layer[0].find_elements_by_tag_name("input")
            if (len(button_layer) == 0):
                continue

            for button in button_layer:
                if (button.is_displayed()):
                    time.sleep(0.25)
                    if (button.is_enabled()):
                        button.click()
                
                #print("is visisble: ", first_row_check_input[i].is_displayed())
                #print("is enabled: ", first_row_check_input[i].is_enabled())
                #print("input ", i, ": ", first_row_check_input[i].get_attribute("outerHTML"))

        # click enroll button
        enroll_button_xpath = r'//*[@id="DERIVED_REGFRM1_LINK_ADD_ENRL$291$"]'
        enroll_button_webElement = driver.find_element_by_xpath(enroll_button_xpath)
        if (enroll_button_webElement.is_enabled() and enroll_button_webElement.is_displayed()):
            enroll_button_webElement.click()

            # check if error message is visible
            error_img_xpath = r'/html/body/div[1]/div/div/span/span/div/form/div[5]/table/tbody/tr/td/div/table/tbody/tr[8]/td[2]/div/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/div/a/img'
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located( (By.XPATH, error_img_xpath) )
                )
                print("Enroll failed, sleeping for ", sleep_time_bound, " seconds")
                
                # sleep 1/10 of second and check if we are not 30 seconds before target time
                for i in range(sleep_time_bound*10):
                    now = datetime.datetime.now()
                    #print("now: ", now)
                    if (now.hour <= target_time_hr and (now.minute < target_time_min or (now.minute == target_time_min-1 and now.second < 45)) ):
                        #print("sleeping")
                        time.sleep(0.1)
                    else:
                        break

                sleep_time_bound *= 2

                # REMOVE IN REAL USAGE
                #first_sem_success = True
            except:
                #print("")
                finish_enrolling_xpath = r'//*[@id="DERIVED_REGFRM1_SSR_PB_SUBMIT"]'
                finish_enrolling_element = get_element(driver, finish_enrolling_xpath, 15)
                if (is_button_clickable(finish_enrolling_element)):
                    finish_enrolling_element.click()
                    time.sleep(0.5)
                    if (not first_sem_success):
                        print("succesfully enrolled to fall semester")
                    else:
                        print("succesfully enrolled to winter semester")

                if (not first_sem_success):
                    first_sem_success = True
                else:
                    break

    
    #assert "No Results found." in driver.page_source
    print("Stopping program")
    driver.close()
    sys.exit(0)

    
schedule.every().day.at(target_time).do(enroll)

while(True):
    schedule.run_pending()
    time.sleep(1)
