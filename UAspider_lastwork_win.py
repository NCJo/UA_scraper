# TODO: fully customized input

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json
import io

# check whether current flight is already in the record
def flightNumberReplication(flRepArr, flNum):
    if flNum not in flRepArr:
        flRepArr.append(flNum)
        flRepArr[:] = flRepArr
        return True
    else:
        return False

dataArr = []
day = 10
repeat = int(input("number of days: "))

for i in range(repeat):
    path_to_chromedriver = "F:\workspace\chromedriver.exe"
    browser = webdriver.Chrome(executable_path=path_to_chromedriver)

    day += i
    url = 'https://www.united.com/ual/en/us/flight-search/book-a-flight/results/rev?f=ORD&t=ATL&d=2017-07-' + str(day) + '&tt=1&sc=7&px=1&taxng=1&idx=1'

    browser.get(url)
    time.sleep(10)

    # expand to see all flights

    expand = browser.find_element_by_xpath('//*[@id="fl-results-pagerShowAll"]')
    ActionChains(browser).move_to_element(expand).send_keys(Keys.PAGE_DOWN).perform()
    ActionChains(browser).move_to_element(expand).send_keys(Keys.PAGE_DOWN).perform()
    time.sleep(2)   # wait for page scrolling
    try:
        browser.find_element_by_xpath('//*[@id="fl-results-pagerShowAll"]').click()
    except:
        print("No show all")
        pass

    time.sleep(5)   # load all the available planes
    visitedSeatIDArr = []
    allSeatsToCountArr = []
    occupiedSeatsToCountArr = []
    visitedFlightReplicate = []
    ActionChains(browser).send_keys(Keys.HOME).perform()
    time.sleep(1)

    # click detailed view
    browser.find_element_by_xpath('//*[@id="fl-search-header-wrap"]/div[2]/div[1]/div/div/label[2]').click()
    time.sleep(2)
    # get flight numbers
    flightNumbers = browser.find_elements_by_class_name('segment-flight-number')
    # get total number of flights
    totalNumOfFlights = browser.find_elements_by_class_name('flight-block-fares-container')
    # get number of connections
    flightConnections = browser.find_elements_by_class_name('flight-connection-container')
    # get all flights' seat map links
    allSeatLinks = browser.find_elements_by_class_name('toggle-flight-block-seats')

    for seatLink in allSeatLinks:
        # wait until element is visible
        visible = WebDriverWait(browser, 10).until(EC.visibility_of(seatLink))
        browser.execute_script("return arguments[0].scrollIntoView();", seatLink)
        browser.execute_script("window.scrollBy(0, -150);")
        visible.click()
        time.sleep(5)
        # plane type and flight number (read after click on "Seats")
        planeType = browser.find_elements_by_class_name('equipment-type')
        time.sleep(2)

        # match read connection flights to return correct flight numbers
        connection = re.findall(r'\b\d+\b',  flightConnections.pop(0).text)
        if len(connection) != 0:
            numOfConnection = int(connection.pop())
            numOfFlightConnectionJSON = numOfConnection
            flNum = flightNumbers.pop(0).text
            flNumJSON = flNum[7:]
            print(flNum[7:])
            for i in range(numOfConnection):
                flightNumbers.pop(0)
        else:
            numOfFlightConnectionJSON = 0
            flNum = flightNumbers.pop(0).text
            flNumJSON = flNum[7:]
            print(flNum[7:])
        # need try statement for plane type
        planeTypeJSON = planeType[-1].text
        print(planeType[-1].text)
        time.sleep(1)
        allSeats = browser.find_elements_by_class_name('seat')
        allOccupiedSeats = browser.find_elements_by_class_name('occupied')
        if flightNumberReplication(visitedFlightReplicate, flNum):
            for allSeatID in allSeats:
                if allSeatID._id not in visitedSeatIDArr:
                    visitedSeatIDArr.append(allSeatID._id)
                    allSeatsToCountArr.append(allSeatID)
            for occupiedSeatID in allOccupiedSeats:
                if occupiedSeatID._id not in visitedSeatIDArr:
                    visitedSeatIDArr.append(occupiedSeatID._id)
                    occupiedSeatsToCountArr.append(occupiedSeatID)
            # all the calculations for seats
            totalSeatsJSON = len(allSeatsToCountArr)
            occupiedSeatsJSON = len(occupiedSeatsToCountArr)
            emptySeatsJSON = len(allSeatsToCountArr) - len(occupiedSeatsToCountArr)

            print("Empty = ", len(allSeatsToCountArr) - len(occupiedSeatsToCountArr), " || Occupied = ", len(occupiedSeatsToCountArr))
            print("")

            try:
                data = {
                    'a. flight number': flNumJSON,
                    'b. model': planeTypeJSON,
                    'c. total seats': totalSeatsJSON,
                    'd. occupied seats': occupiedSeatsJSON,
                    'e. empty seats': emptySeatsJSON,
                    'f. number of connection flights': numOfFlightConnectionJSON
                }
                dataArr.append(data)

                allSeatsToCountArr = []
                occupiedSeatsToCountArr = []
                time.sleep(2)
            except:
                print("No data to record")
                pass

        else:
            print("Replicate Flight: not record")
            print("")
            pass

        # # all the calculations for seats
        # totalSeatsJSON = len(allSeatsToCountArr)
        # occupiedSeatsJSON = len(occupiedSeatsToCountArr)
        # emptySeatsJSON = len(allSeatsToCountArr) - len(occupiedSeatsToCountArr)
        #
        # print("Empty = ", len(allSeatsToCountArr) - len(occupiedSeatsToCountArr), " || Occupied = ", len(occupiedSeatsToCountArr))
        # print("")

        seatLink.click()
        time.sleep(1)


    with io.open('UAdata.json', 'a', encoding='utf8') as outfile:
        str_ = json.dumps(dataArr,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(str_)

    allSeats = []
    allOccupiedSeats = []
    dataArr = []
    visitedFlightReplicate = []
    browser.close()



"""
# type of airplane
planeType = browser.find_elements_by_class_name('equipment-type')
print('planeType', planeType[-1].text)

# check day: a[4=today, 5=tomorrow], div[1] = day (Thu 6/20)
nextDay = browser.find_element_by_xpath('//*[@id="farewheel-placeholder"]/div/div/div/a[4]/div[1]').text
print(nextDay)

# WORKING: find all seats in a plane
seats = browser.find_elements_by_xpath('//*[contains(@id, "spanSeat")]/span')
empty = 0
occupied = 0
for i in seats:
    #print(i.text)
    if i.text == "Occupied":
        occupied += 1
    else:
        empty += 1
print("Empty = ", empty, " || Occupied = ", occupied)

# find single seat
# seat = browser.find_element_by_xpath('//*[@id="spanSeat21D"]/span')
# print(seat.text)

# find all seats in a plane
# seats = browser.find_elements_by_xpath('//*[contains(@id, "spanSeat")]/span')

# click element outside webview
# ActionChains(browser).move_to_element(seatLink).click().perform()

# instead of using time.sleep()
# test = WebDriverWait(browser, 10).until(EC.visibility_of(seatLink))
# test.click()

# specifically get rid of the word "flight"
# flNum = re.finadall(r'\b(?!\FLIGHT\b)\w)+\b', flightNumbers.pop(0).text)
"""