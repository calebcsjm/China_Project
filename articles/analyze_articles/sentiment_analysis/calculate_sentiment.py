from transformers import pipeline
import multiprocessing
import pandas as pd
import csv
import os

BASE_QUARTER_SAVE_FOLDER = '/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/analyze_articles/sentiment_analysis/quarter_sentiments/'
AGGREGATE_SAVE_FOLDER = '/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/analyze_articles/sentiment_analysis/aggregated_sentiments_2.0/'

sentiment_model = pipeline(
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", 
    top_k=None
)

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
    
def calculate_term_sentiment(df, term):
    """Calculates average sentiment for sentences containing the term across a dataframe.
    
    Intended for use on one quarter at a time"""

    print(f"Articles in quarter: {len(df)}")

    # store average sentiment scores for each sentence in the df with the term
    pos_scores = []
    neu_scores = []
    neg_scores = []

    counter = 1
    for index, row in df.iterrows():
        # add in a progress check
        counter += 1
        if counter % 100 == 0:
            print(f"Analyzed {counter}/{len(df)} articles")

        # verify the text has the term, if not skip
        text = row["text"]
        if not is_valid_row(text, term):
            continue

        sentences = get_split_sentences(text)

        # get the sentences with the term
        sentences_w_term = [sentence for sentence in sentences if term in sentence]

        # iterate over all the sentences in the article that contain the term
        for sentence in sentences_w_term:
            try:
                # calculate sentiment scores for that sentence
                sentiment_scores = sentiment_model(sentence)

                # add the scores to the quarter's lists
                # if the sentence had n uses of the term, duplicated it n times, so sentences with more uses are given more weight
                sentence_term_count = sentence.count(term)
                pos_scores.extend([sentiment_scores[0][0]['score']] * sentence_term_count)
                neu_scores.extend([sentiment_scores[0][1]['score']] * sentence_term_count)
                neg_scores.extend([sentiment_scores[0][2]['score']] * sentence_term_count)
            except:
                print(f"Sentiment analysis failed on sentence: {sentence}")

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


def worker(df, quarter, term, save_folder):
    '''Worker that calculates the sentiment in a quarter and saves the results in a csv'''
    # initial check
    print(f'df len: {len(df)}, quarter: {quarter}, term: {term}')

    # calculate the sentiment results
    sentiment_results = calculate_term_sentiment(df, term)

    # add the quarter to the results dictionary
    sentiment_results['year_quarter'] = quarter

    # convert the dictionary results to a csv file and save
    with open(f'{save_folder}/{quarter}.csv', 'w') as f:  
        w = csv.DictWriter(f, sentiment_results.keys())
        w.writeheader()
        w.writerow(sentiment_results)

    print(f"Worker \"{quarter}\": Completed processing {len(df)} articles")


def join_quarterly_sentiments(quarter_save_folder, publisher, term):
    '''Iterate over all the csv files in the folder we generated, and combine them into one'''
    dfs = []
    files = os.listdir(quarter_save_folder)

    # Iterate over each file
    for file_name in files:
        # Construct the full file path
        file_path = os.path.join(quarter_save_folder, file_name)
        temp_df = pd.read_csv(file_path)
        dfs.append(temp_df)

    result = pd.concat(dfs, ignore_index=True)
    result = result.sort_values(by='year_quarter')
    result.to_csv(f'{AGGREGATE_SAVE_FOLDER}/{publisher}_{term}.csv', index=False)


def calculate_magazine_sentiment(article_path, term, publisher):
    # Create a new directory
    new_directory = BASE_QUARTER_SAVE_FOLDER + "/" + publisher + "/" + term
    os.makedirs(new_directory, exist_ok=True)

    # Store the file path for the directory
    quarter_save_folder = os.path.abspath(new_directory)

    # get the data
    print("Loading articles...")
    articles = pd.read_csv(article_path)
    print("Loaded CSV")

    # define the list of quarter names
    quarters = sorted(articles['year_quarter'].unique())
    print(f'Quarters: {quarters}')

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
    pool.starmap(worker, zip(dfs, quarters, [term] * len(quarters), [quarter_save_folder] * len(quarters)))

    # Close the pool to prevent any more tasks from being submitted
    pool.close()

    # Wait for all processes to complete
    pool.join()

    # join the resulting files into one 
    join_quarterly_sentiments(quarter_save_folder, publisher, term)


if __name__ == "__main__":
    # analyze QS
    calculate_magazine_sentiment("/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/process_articles/process_qiushi_articles/validated_qiushi_articles.csv",
                                 '一带一路',
                                 "QS")
    calculate_magazine_sentiment("/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/process_articles/process_qiushi_articles/validated_qiushi_articles.csv",
                                 '全球发展倡议',
                                 "QS")
    calculate_magazine_sentiment("/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/process_articles/process_qiushi_articles/validated_qiushi_articles.csv",
                                 '经济',
                                 "QS")
    
    # analyze ASX
    calculate_magazine_sentiment("/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/process_articles/process_asx_articles/validated_asx_articles.csv",
                                 '一带一路',
                                 "ASX")
    calculate_magazine_sentiment("/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/process_articles/process_asx_articles/validated_asx_articles.csv",
                                 '全球发展倡议',
                                 "ASX")
    calculate_magazine_sentiment("/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/process_articles/process_asx_articles/validated_asx_articles.csv",
                                 '美国',
                                 "ASX")
    calculate_magazine_sentiment("/Users/calebharding/Documents/BYU/2023-2024/China_Project/articles/process_articles/process_asx_articles/validated_asx_articles.csv",
                                 '经济',
                                 "ASX")
    

    