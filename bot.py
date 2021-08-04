from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import time, datetime
import pytz
from time import gmtime, strftime
import beepy as beep
import getopt, sys
import os

argumentList = sys.argv[1:]
# Options
options = "hs:d:c:"

state = ''
district = ''
check18up = False
dd2 = 5 # set a pre-filtetr for dose2, currently it is set to 5 this means that a new center with more than or equal to 5 vaccine slots will show in alert
dd1 = 4 # set a pre-filtetr for dose1, currently it is set to 4 this means that a new center with more than or equal to 4 vaccine slots will show in alert
# Long options
long_options = ["Help", "State=", "District=", "Check18up"]

try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)

    # checking each argument
    for currentArgument, currentValue in arguments:

        if currentArgument in ("-h", "--Help"):
            print ("Diplaying Help")
            print('Use -s to enter state name')
            print('Use -d to enter district name')
            print('Set -c to enable 18+ filter to True')
        elif currentArgument in ("-s", "--State"):
            # print ("Displaying file_name:", sys.argv[0])
            state = currentValue
            # print(currentValue)

        elif currentArgument in ("-d", "--District"):
            district = currentValue
            # print(currentValue)

        elif currentArgument in ("-c", "--Check18up"):
            check18up = currentValue
            # print(currentValue)
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))

print('Entered State:'+state)
print('Entered District:'+district)
print('Check18up:'+str(check18up))

url = 'https://www.cowin.gov.in/'

sound = 6


def alert(x):
    beep.beep(x)

def setupCowin(browser,state,district):
    # click to get state and district
    browser.get(url)
    time.sleep(1)
    loc_button = browser.find_element_by_xpath("//*[contains(text(), 'Search by District')]")
    loc_button.click()
    time.sleep(1)
    search_tab = browser.find_element_by_xpath("//div[@class='searchdistwrper ng-star-inserted']")

    state_box = search_tab.find_element_by_xpath("//mat-select[@formcontrolname='state_id']")
    state_box.click()
    time.sleep(1.5)
    state_lists = browser.find_element_by_xpath("//div[@role='listbox']").find_elements_by_xpath("//span[@class='mat-option-text']")
    print('Selected Region')
    for i in state_lists:
        target = i.text
        if(target.lower() == state.lower()):
            print('State: '+i.text)
            i.click()
            break
    time.sleep(2)


    district_box = search_tab.find_element_by_xpath("//mat-select[@formcontrolname='district_id']")
    district_box.click()
    time.sleep(2)
    district_list = district_box.find_element_by_xpath("//div[@role='listbox']").find_elements_by_xpath("//span[@class='mat-option-text']")
    for i in district_list:
        target = i.text
        if(target.lower() == district.lower()):
            print('District: '+i.text)
            i.click()
            break

    time.sleep(1)
    search_btn = browser.find_element_by_xpath("//button[@class='pin-search-btn district-search']")
    search_btn.click()
    time.sleep(2)
    return browser

def check_slots(browser,state,district):

    available = False
    while(not available):
        # alert(1)
        browser = setupCowin(browser,state,district)

        main_box = browser.find_element_by_xpath("//div[@class='center-box']")
        desired_y = (main_box.size['height'] / 2) + main_box.location['y']
        current_y = (browser.execute_script('return window.innerHeight') / 2) + browser.execute_script('return window.pageYOffset')
        scroll_y_by = desired_y - current_y
        browser.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)

        all_center = main_box.find_elements_by_xpath("//div[@class='row ng-star-inserted']")

        for center in all_center:

            info = center.text.split('\n')
            center_name = info[0]
            center_address = info[1]
            print('Checking at- '+str(center_name)+' ['+str(center_address.split(" ")[-1])+']')

            for i in range(2,len(info[2:])):

                time_IND = pytz.timezone("Asia/Calcutta")
                curr_time = datetime.datetime.now(time_IND).strftime("%Y-%m-%d %H:%M:%S")
                if(info[i] == 'NA'):
                    pass
                elif(info[i] == 'Booked'):
                    age = info[i+2]
                    vacc_type = info[i+1]

                    print('Booked ', vacc_type,': ',age)

                    i+=3
                try:
                    if(info[i] == 'D1'):
                        dose1 = info[i+1]
                        totalvacc = info[i+2]
                        dose2 = info[i+4]
                        vacc_type = info[i+5]
                        age = info[i+6]

                        if(int(dose1)<dd1):
                            i+=7
                            continue
                        print('-'*20)
                        print('Slots available:'+totalvacc+ ' <<<<<>>>>> Vaccine: '+vacc_type)
                        print('D1- '+dose1+'  '+'D2- '+dose2)
                        print('At Center: '+center_name)
                        print('Pin Code:  ---------['+str(center_address.split(" ")[-1])+ ']---------')
                        pincode = str(center_address.split(" ")[-1])
                        print('Location: '+center_address)
                        if (vacc_type == 'COVAXIN'):
                            local = [curr_time,' || '+str(center_address.split(" ")[-1]),' || ('+vacc_type+')','|| Slots- '+totalvacc, 'Dose1- '+dose1, 'Dose2- '+dose2, ' || Name- '+center_name, ' ||'+center_address,' \n']
                            if(os.path.isfile('Covaxin_'+state+'_'+district+'_'+str(check18up)+'.txt')):
                                with open('Covaxin_'+state+'_'+district+'_'+str(check18up)+'.txt','a+') as file:
                                    file.writelines(local)
                            else:
                                with open('Covaxin_'+state+'_'+district+'_'+str(check18up)+'.txt','w+') as file:
                                    file.writelines(local)

                            for k in range(2):
                                alert(sound)

                        else:
                            # alert(1)
                            local = [curr_time,' || '+str(center_address.split(" ")[-1]),' || ('+vacc_type+')','|| Slots- '+totalvacc, ' || Dose1- '+dose1, ' || Dose2- '+dose2, ' || Name- '+center_name, ' ||'+center_address, ' \n']
                            if(os.path.isfile('Covishield_'+state+'_'+district+'_'+str(check18up)+'.txt')):
                                with open('Covishield_'+state+'_'+district+'_'+str(check18up)+'.txt','a+') as file:
                                    file.writelines(local)
                            else:
                                with open('Covishield_'+state+'_'+district+'_'+str(check18up)+'.txt','w+') as file:
                                    file.writelines(local)
                        print('-'*20)
                    i+=7

                except:
                    pass
            if(not available):
                print('No slots available at')

        print('Will Recheck after 15sec')
        time.sleep(15)

while(True):
    browser = webdriver.Chrome('./chromedriver')
    try:
        check_slots(browser,state,district)
    except:
        browser.quit()
        print('Some Error, Retrying...')
        # time.sleep(5)
        continue
