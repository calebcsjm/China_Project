import multiprocessing
import pandas as pd

import sys
sys.path.append('/Users/calebharding/Documents/BYU/2023-2024/China_Project/analyze_articles')
from sentiment_analysis import calculate_sentiment

def worker(df, quarter):
    """Simple function to simulate work."""
    # result = num * num
    quarter = quarter.replace(" ", "_")

    sentiment_results = calculate_sentiment(df, '经济')

    with open(f'/Users/calebharding/Documents/BYU/2023-2024/China_Project/multiprocessing_practice/outputs/{quarter}.txt', 'w') as f:
        f.write(f"Worker \"{quarter}\": Result is {sentiment_results}")

    print(f"Worker \"{quarter}\": Result is {len(df)}")

if __name__ == "__main__":

    # get the data
    print("Loading articles...")
    df = pd.read_csv('./process_asx_articles/asx_sample.csv')
    print("Loaded CSV")
    quarters = sorted(df['year_quarter'].unique())
    print(f'Quarters: {quarters}')
    quarters_w_df = []
    for quarter in quarters:
        temp_df = df[df['year_quarter'] == quarter]
        quarters_w_df.append((temp_df, quarter))

    # Number of processes to create
    num_processes = multiprocessing.cpu_count()

    # Create a pool of processes
    pool = multiprocessing.Pool(processes=num_processes)

    # Map the worker function to the pool of processes
    # Each process will execute the worker function with a different argument
    pool.starmap(worker, quarters_w_df)

    # Close the pool to prevent any more tasks from being submitted
    pool.close()

    # Wait for all processes to complete
    pool.join()