import streamlit as st
import pandas as pd
import os

# Define the directory containing the company data
data_dir = r'C:\Users\ibrahim.fadhili\Downloads\NSE Project\data\company'

# Get a list of all CSV files in the directory
company_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

# Remove file extensions to use as company names in the dropdown
companies = [os.path.splitext(f)[0] for f in company_files]

# Streamlit app
st.title('Company Data Viewer')

# Dropdown to select a company
selected_company = st.selectbox('Select a company', companies)

# Get the file corresponding to the selected company
selected_file = os.path.join(data_dir, f"{selected_company}.csv")

try:
    # Load the data into a DataFrame
    df = pd.read_csv(selected_file, sep=',')

    # Remove null values
    df.dropna(inplace=True)
    
    # Reset the index after dropping rows
    df.reset_index(drop=True, inplace=True)
    
    # Rename columns to match the provided format
    df.columns = ['Date', 'Low', 'High', 'Clos3', 'Open', 'Volume']
    
    # Convert the 'Date' column from YYYYMMDD to MM/DD/YYYY format
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d').dt.strftime('%m/%d/%Y')
    
    # Display the DataFrame with renamed columns
    st.dataframe(df)
except Exception as e:
    st.error(f"Error loading or processing the file: {e}")
