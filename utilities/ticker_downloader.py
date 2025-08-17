import yfinance as yf

# df = yf.Ticker("STLAM.MI").history(period="1mo", interval="30m")
price = yf.Ticker("STLAM.MI").fast_info
print(price)
print(price["lastPrice"])
# df.reset_index(inplace=True)

# df.to_csv(r'C:\Users\gianm\OneDrive\Desktop\ticker.csv', index=False)
