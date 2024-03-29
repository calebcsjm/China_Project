from transformers import pipeline

sentiment_model = pipeline(
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", 
    return_all_scores=True
)

def is_valid_row(text, term):
    # this article has text
    if type(text) != str:
        return False
    
    # the word is contained in the text
    count = text.count(term)
    if count == 0:
        return False
    
    return True

def get_split_sentences(text):
    # replace possible sentence endings with periods, then split on periods
    text = text.replace("？", "。")
    text = text.replace("！", "。")
    text = text.replace("；", "。")
    text = text.replace(".", "。")

    return text.split("。")

def list_average(list):
    return sum(list) / len(list)
    
def calculate_sentiment(df, term):
    """Calculates average sentiment for sentences containing the term across an entire dataframe"""

    print(f"Articles in quarter: {len(df)}")

    pos_scores = []
    neu_scores = []
    neg_scores = []

    for index, row in df.iterrows():
        text = row["text"]
        if not is_valid_row(text, term):
            continue

        sentences = get_split_sentences(text)

        # get the sentences with the term
        sentences_w_term = [sentence for sentence in sentences if term in sentence]

        # sentiment of each sentence
        # average for article using the number of sentences
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

        article_avg_pos = list_average(positive_sent_scores)
        article_avg_neu = list_average(neutral_sent_scores) 
        article_avg_neg = list_average(negative_sent_scores) 

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
        
    