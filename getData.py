import os
import shutil
import streamlit as st
from src import *

# Initialize the classes
crawler = Crawler()
calender = Calender()
formatter = FormatData()

# Set the date range
startYear = 2016
startMonth = 1
endYear = 2024
endMonth = 12

st.title("Financial Data Crawler and Formatter")

st.write("## Preparing Daily Data")
daily_progress_bar = st.progress(0)
total_months = (endYear - startYear + 1) * 12
current_month = 0

while startYear < (endYear + 1):
    st.write(f"### Year {startYear}")
    while startMonth < 13:
        st.write(f"#### Month: {startMonth}")
        month = calender.getDayInMonth(startYear, startMonth)
        for day in month:
            crawler.getURLData(int(day))
        if startMonth == endMonth and startYear == endYear:
            break
        startMonth += 1
        current_month += 1
        daily_progress_bar.progress(current_month / total_months)
    startMonth = 1
    startYear += 1

# Clean up and create directories for monthly, yearly, and company data
for folder in ['monthly', 'yearly', 'company']:
    shutil.rmtree('data/' + folder, ignore_errors=True, onerror=None)
    os.mkdir('data/' + folder)

pathDaily = 'data/daily/'
pathYearly = 'data/yearly/'
pathMonthly = 'data/monthly/'
pathCompany = 'data/company/'

# Create monthly data
st.write("## Preparing Monthly Data")
formatter.getMonthlyData(pathDaily, pathMonthly)

# Create yearly data
st.write("## Preparing Yearly Data")
formatter.getYearlyData(pathMonthly, pathYearly)

# Create company data
st.write("## Preparing Company Data")
formatter.getCompanyData(pathYearly, pathCompany)

st.success("Process Completed !!")
