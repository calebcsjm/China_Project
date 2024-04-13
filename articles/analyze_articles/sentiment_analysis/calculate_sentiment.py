from transformers import pipeline
import multiprocessing
import pandas as pd
import csv
import os

sentiment_model = pipeline(
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", 
    top_k=None
)

BASE_SAVE_FOLDER = '/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/analyze_articles/sentiment_analysis/quarter_sentiments/'
ARTICLE_PATH = '/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/process_articles/process_asx_articles/validated_asx_articles.csv'
AGGREGATE_SAVE_FOLDER = '/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/analyze_articles/sentiment_analysis/aggregated_sentiments/'
TERM = '经济'
PUBLISHER = 'ASX'

# Create a new directory
new_directory = BASE_SAVE_FOLDER + "/" + PUBLISHER + "/" + TERM
os.makedirs(new_directory, exist_ok=True)
# Store the file path for the directory
SAVE_FOLDER = os.path.abspath(new_directory)

def is_valid_row(text, term):
    '''Verifies that the article has text and contains the word'''
    # this article has text
    if type(text) != str:
        return False
    
    # the word is contained in the text
    count = text.count(term)
    if count == 0:
        return False
    
    return True

def get_split_sentences(text):
    '''Replaces possible sentence endings with periods, then returns list of sentences'''

    sentence_ends = ["？", "?", "！", "!", "；", ";", ".", "（", "(", ")", "）", ":", "："]

    for punct in sentence_ends:
        text = text.replace(punct, "。")

    return text.split("。")

def list_average(list):
    return sum(list) / len(list)
    
def calculate_sentiment(df, term):
    """Calculates average sentiment for sentences containing the term across a dataframe.
    
    Intended for use on one quarter at a time"""

    print(f"Articles in quarter: {len(df)}")

    # store average sentiment scores for each article in the df
    pos_scores = []
    neu_scores = []
    neg_scores = []

    counter = 1
    for index, row in df.iterrows():
        # add in a progress check
        counter += 1
        if counter % 100 == 0:
            print(f"Analyzed {counter}/{len(df)} articles")

        text = row["text"]
        if not is_valid_row(text, term):
            continue

        sentences = get_split_sentences(text)

        # get the sentences with the term
        sentences_w_term = [sentence for sentence in sentences if term in sentence]

        # sentiment of each sentence
        positive_sent_scores = []
        neutral_sent_scores = []
        negative_sent_scores = []

        for sentence in sentences_w_term:
            try:
                sentiment_scores = sentiment_model(sentence)
                positive_sent_scores.append(sentiment_scores[0][0]['score'])
                neutral_sent_scores.append(sentiment_scores[0][1]['score'])
                negative_sent_scores.append(sentiment_scores[0][2]['score'])
            except:
                print(f"Sentiment analysis failed on sentence: {sentence}")

        # average for article using the number of sentences
        article_avg_pos = list_average(positive_sent_scores)
        article_avg_neu = list_average(neutral_sent_scores) 
        article_avg_neg = list_average(negative_sent_scores) 

        # append article scores to df list
        pos_scores.append(article_avg_pos)
        neu_scores.append(article_avg_neu)
        neg_scores.append(article_avg_neg)


    try:
        avg_pos = list_average(pos_scores) 
        avg_neu = list_average(neu_scores) 
        avg_neg = list_average(neg_scores)
    except:
        avg_pos = None
        avg_neu = None
        avg_neg = None

    results = {"positive":avg_pos, "neutral":avg_neu, "negative":avg_neg}
    
    return results


def worker(df, quarter, term):
    '''Worker that calculates the sentiment in a quarter and saves the results in a csv'''
    # initial check
    print(f'df len: {len(df)}, quarter: {quarter}, term: {term}')

    # quarter = quarter.replace(" ", "_")

    # calculate the sentiment results
    sentiment_results = calculate_sentiment(df, term)

    # add the quarter to the results dictionary
    sentiment_results['year_quarter'] = quarter

    # convert the dictionary results to a csv file and save
    with open(f'{SAVE_FOLDER}/{quarter}.csv', 'w') as f:  
        w = csv.DictWriter(f, sentiment_results.keys())
        w.writeheader()
        w.writerow(sentiment_results)

    print(f"Worker \"{quarter}\": Completed processing {len(df)} articles")


def join_quarterly_sentiments():
    '''Iterate over all the csv files in the folder we generated, and combine them into one'''
    dfs = []
    files = os.listdir(SAVE_FOLDER)

    # Iterate over each file
    for file_name in files:
        # Construct the full file path
        file_path = os.path.join(SAVE_FOLDER, file_name)
        temp_df = pd.read_csv(file_path)
        dfs.append(temp_df)

    result = pd.concat(dfs, ignore_index=True)
    result.to_csv(f'{AGGREGATE_SAVE_FOLDER}/{PUBLISHER}_{TERM}.csv', index=False)

if __name__ == "__main__":

    # get the data
    print("Loading articles...")
    articles = pd.read_csv(ARTICLE_PATH)
    print("Loaded CSV")

    # define the list of quarter names
    quarters = sorted(articles['year_quarter'].unique())
    print(f'Quarters: {quarters}')

    # create a n-length list of the term
    terms = [TERM] * len(quarters)

    # create a list of the quarters
    dfs = []
    for quarter in quarters:
        temp_df = articles[articles['year_quarter'] == quarter]
        dfs.append(temp_df)

    # Number of processes to create
    num_processes = multiprocessing.cpu_count()

    # Create a pool of processes
    pool = multiprocessing.Pool(processes=num_processes)

    # Map the worker function to the pool of processes
    # Each process will execute the worker function with a different argument
    pool.starmap(worker, zip(dfs, quarters, terms))

    # Close the pool to prevent any more tasks from being submitted
    pool.close()

    # Wait for all processes to complete
    pool.join()

    # join the resulting files into one 
    join_quarterly_sentiments()