import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# Define the directory containing the company data
data_dir = r'C:\Users\ibrahim.fadhili\Downloads\NSE\data\company'

# Get a list of all CSV files in the directory
company_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

# Extract company names from file names
companies = [os.path.splitext(f)[0] for f in company_files]

# Function to calculate ATR
def atr(high, low, close, n=14):
    tr = np.amax(np.vstack(((high - low).to_numpy(), 
                            (abs(high - close)).to_numpy(), 
                            (abs(low - close)).to_numpy())).T, axis=1)
    return pd.Series(tr).rolling(n).mean().to_numpy()

# Function to calculate Bollinger Bands
def calculate_BBANDS(data, window):
    MA = data['Closing Price'].rolling(window=window).mean()
    SD = data['Closing Price'].rolling(window=window).std()
    data['MiddleBand'] = MA
    data['UpperBand'] = MA + (2 * SD)
    data['LowerBand'] = MA - (2 * SD)
    return data

# Function to calculate RSI
def rsi(close, periods=14):
    close_delta = close.diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi

# Function to calculate Force Index
def force_index(data, ndays):
    FI = pd.Series(data['Closing Price'].diff(ndays) * data['Volume Traded'], name='ForceIndex')
    data = data.join(FI)
    return data

# Function to calculate MFI
def mfi(high, low, close, volume, n=14):
    typical_price = (high + low + close) / 3
    money_flow = typical_price * volume
    mf_sign = np.where(typical_price > typical_price.shift(1), 1, -1)
    signed_mf = money_flow * mf_sign

    positive_mf = np.where(signed_mf > 0, signed_mf, 0)
    negative_mf = np.where(signed_mf < 0, -signed_mf, 0)

    mf_avg_gain = pd.Series(positive_mf).rolling(n, min_periods=1).sum()
    mf_avg_loss = pd.Series(negative_mf).rolling(n, min_periods=1).sum()

    return (100 - 100 / (1 + mf_avg_gain / mf_avg_loss)).to_numpy()

def load_data(company):
    file_path = os.path.join(data_dir, f"{company}.csv")
    df = pd.read_csv(file_path)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.columns = ['Date', 'Lowest Price of the Day', 'Highest Price of the Day', 'Closing Price', 'Previous Day Closing Price', 'Volume Traded']
    df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
    df['Lowest Price of the Day'] = pd.to_numeric(df['Lowest Price of the Day'], errors='coerce')
    df['Highest Price of the Day'] = pd.to_numeric(df['Highest Price of the Day'], errors='coerce')
    df['Closing Price'] = pd.to_numeric(df['Closing Price'], errors='coerce')
    df['Volume Traded'] = pd.to_numeric(df['Volume Traded'], errors='coerce')
    return df


# Main function for Streamlit app
def main():
    st.subheader('Technical Indicators')

    selected_company = st.selectbox('Select a company', companies)
    selected_indicator = st.selectbox('Select an Indicator', ['Bollinger Bands', 'ATR', 'RSI', 'Force Index', 'MFI'])

    if selected_company:
        st.subheader(f"{selected_company}'s {selected_indicator}")
        data = load_data(selected_company)

        if selected_indicator == 'History':
            st.dataframe(data)

        elif selected_indicator == 'Bollinger Bands':
            window = st.number_input('Enter window size:', min_value=1, max_value=100, value=20)
            data_with_bbands = calculate_BBANDS(data, window)

            fig, ax = plt.subplots(figsize=(10, 7))
            ax.set_title('Bollinger Bands')
            ax.set_xlabel('Date')
            ax.set_ylabel('Price')
            ax.plot(data_with_bbands['Closing Price'], lw=1, label='Closing Price')
            ax.plot(data_with_bbands['UpperBand'], 'g', lw=1, label='Upper Band')
            ax.plot(data_with_bbands['MiddleBand'], 'r', lw=1, label='Middle Band')
            ax.plot(data_with_bbands['LowerBand'], 'g', lw=1, label='Lower Band')
            ax.legend()
            st.pyplot(fig)

        elif selected_indicator == 'ATR':
            data['ATR'] = atr(data['Highest Price of the Day'], data['Lowest Price of the Day'], data['Closing Price'])
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
            ax1.set_title(f'{selected_company} Price Chart')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Closing Price')
            ax1.plot(data['Date'], data['Closing Price'], label='Closing Price')
            ax1.legend()
            ax2.set_title('Average True Range (ATR)')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('ATR values')
            ax2.plot(data['Date'], data['ATR'], 'm', label='ATR')
            ax2.legend()
            plt.tight_layout()
            st.pyplot(fig)

        elif selected_indicator == 'RSI':
            data['RSI'] = rsi(data['Closing Price'])
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
            ax1.set_title(f'{selected_company} Price Chart')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Closing Price')
            ax1.plot(data['Date'], data['Closing Price'], label='Closing Price')
            ax1.legend()
            ax2.set_title('Relative Strength Index (RSI)')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('RSI values')
            ax2.plot(data['Date'], data['RSI'], 'm', label='RSI')
            ax2.legend()
            plt.tight_layout()
            st.pyplot(fig)

        elif selected_indicator == 'Force Index':
            data = force_index(data, 1)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
            ax1.set_title(f'{selected_company} Price Chart')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Closing Price')
            ax1.plot(data['Date'], data['Closing Price'], label='Closing Price')
            ax1.legend()
            ax2.set_title('Force Index')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Force Index values')
            ax2.plot(data['Date'], data['ForceIndex'], 'm', label='Force Index')
            ax2.legend()
            plt.tight_layout()
            st.pyplot(fig)

        elif selected_indicator == 'MFI':
            data['MFI'] = mfi(data['Highest Price of the Day'], data['Lowest Price of the Day'], data['Closing Price'], data['Volume Traded'])
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
            ax1.set_title(f'{selected_company} Price Chart')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Closing Price')
            ax1.plot(data['Date'], data['Closing Price'], label='Closing Price')
            ax1.legend()
            ax2.set_title('Money Flow Index (MFI)')
            ax2.set_xlabel('Date')
            ax2.set_ylabel('MFI values')
            ax2.plot(data['Date'], data['MFI'], 'm', label='MFI')
            ax2.legend()
            plt.tight_layout()
            st.pyplot(fig)

if __name__ == '__main__':
    main()
