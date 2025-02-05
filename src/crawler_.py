import os
import csv
import logging
import datetime
import urllib.error as error
import urllib.request as rq
from bs4 import BeautifulSoup
import ssl

class Crawler:
    def __init__(self):
        # Log errors for pages not found
        logging.basicConfig(filename='errorlog/error.log', level=logging.ERROR)
        # Create an unverified SSL context
        self.context = ssl._create_unverified_context()

    def getURLData(self, date):
        '''
                The list dailyShares contains all the companies shares of that day.
                shareDetails list contains all the details of a particular company i.e., name, code, volume, etc.
                shareElement list makes up the Share Details which make up the dailyShares list.
        '''
        self.dailyShares = list()
        self.date = str(date)
        self.createFolder('data/daily/' + self.date[0:4])
        url = "https://live.mystocks.co.ke/" + self.date
        try:
            html = rq.urlopen(url, context=self.context).read()
            self.soup = BeautifulSoup(html, "lxml")
            self.extractURLData()
        except error.HTTPError as e:
            now = datetime.datetime.now()
            errorMessage = str(now) + ' - ' + str(e) + ' Date: ' + str(self.date)
            print('Please check error log file in errorlog directory')
            logging.error(errorMessage)
        except error.URLError as e:
            now = datetime.datetime.now()
            errorMessage = str(now) + ' - ' + str(e) + ' Date: ' + str(self.date)
            print('Please check error log file in errorlog directory')
            logging.error(errorMessage)

    # Extract the data from the page requested
    def extractURLData(self):
        table = self.soup.find("table", {"class": "tblHoverHi"})
        if table is None:
            print(f"No table found for date {self.date}. Skipping.")
            logging.error(f"No table found for date {self.date}.")
            return

        for row in table.findAll("tr"):
            shareDetails = list()
            shareElements = list()
            for element in row.findAll("td"):
                # The share categories i.e., banking, manufacturing
                for heading in element.findAll("h3"):
                    _heading = heading.string
                # The share company name
                for item in element.findAll("a"):
                    shareElements.append(item.string)
                # The shares details i.e., price, volume
                if element.string != heading.string:
                    shareElements.append(element.string)
            # Removes empty and None arrays, clean up from HTML extracted data
            if shareElements and len(shareElements) > 1:
                # Code
                shareDetails.append(shareElements[0])
                # Name
                shareDetails.append(shareElements[1])
                # Lowest price
                if shareElements[5] is None or shareElements[5] == '-':
                    shareDetails.append(shareElements[5])
                else:
                    shareDetails.append(float(shareElements[5].replace(',', '')))
                # Highest price
                if shareElements[6] is None or shareElements[6] == '-':
                    shareDetails.append(shareElements[6])
                else:
                    shareDetails.append(float(shareElements[6].replace(',', '')))
                # Price
                if shareElements[7] is None or shareElements[7] == '-':
                    shareDetails.append(shareElements[7])
                else:
                    shareDetails.append(float(shareElements[7].replace(',', '')))
                # Previous day's price
                if shareElements[8] is None or shareElements[8] == '-':
                    shareDetails.append(shareElements[8])
                else:
                    shareDetails.append(float(shareElements[8].replace(',', '')))
                # Volume
                if shareElements[12] is None or shareElements[12] == '-':
                    shareDetails.append(shareElements[12])
                else:
                    shareDetails.append(str(shareElements[12].replace(',', '')))
                self.dailyShares.append(shareDetails)
        self.saveCSV()

    # Creates a folder for either the year or month if it doesn't exist
    def createFolder(self, path):
        folder = os.path.isdir(path)
        if not folder:
            os.mkdir(path)

    # Saves the data extracted in a CSV
    def saveCSV(self):
        year = self.date[0:4]
        month = self.date[4:6]
        path = 'data/daily/' + str(year) + '/' + month + '/'
        folder = os.path.isdir(path)
        if not folder:
            os.mkdir(path)
        myFile = open(path + str(self.date) + '.csv', 'w', newline='')
        writeFile = csv.writer(myFile, delimiter=';')
        writeFile.writerow(['Code', 'Name', 'Lowest Price of the Day', 'Highest Price of the Day',
                            'Closing Price', 'Previous Day Closing Price', 'Volume Traded'])
        writeFile.writerows(self.dailyShares)
        myFile.close()
