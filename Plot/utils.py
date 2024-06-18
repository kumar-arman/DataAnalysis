import pandas as pd
import matplotlib.pyplot as plt

def read_excel_file(file_path):
    df = pd.read_excel(file_path)
    return df

def plot_data(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df['2019-20'], df['march'])  # Replace with actual column names
    plt.xlabel('2019-20')
    plt.ylabel('march')
    plt.title('Plot of 2019-20 vs march')
    plt.grid(True)
    plt.savefig('myapp/static/myapp/plot.png')  # Save plot as an image file
    plt.close()