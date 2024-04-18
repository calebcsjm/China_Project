
# General Calculations

def get_articles_per_quarter(df):
    articles_per_quarter = {}

    for quarter in df['year_quarter'].unique():
        articles_per_quarter[quarter] = len(df[df['year_quarter'] == quarter])

    articles_per_quarter = dict(sorted(articles_per_quarter.items()))
    return articles_per_quarter

# Frequency Functions

def get_empty_quarters_dict(df):
    quarters_dict = {}

    for quarter in df["year_quarter"].unique():
        quarters_dict[quarter] = 0
        
    return quarters_dict

def quarter_count(articles_df, search_term, standardize=False) -> dict:
    """Returns the number of instances that a give term appears in each quarter. 
    
    If it is standardized, it will divide the number of instances by the number of articles in that quarter,
    to provide more even comparison between quarters and publications. """

    term_quarter_count = get_empty_quarters_dict(articles_df)

    for index, row in articles_df.iterrows():
        year_quarter = row["year_quarter"]
        try: 
            quarter_count = term_quarter_count[year_quarter]
            count = row['text'].count(search_term)
            quarter_count += count
            term_quarter_count[year_quarter] = quarter_count
        except:
            pass

    # sort the years
    term_quarter_count = dict(sorted(term_quarter_count.items()))

    # standardize if specificed
    if standardize:
        articles_per_quarter = get_articles_per_quarter(articles_df)
        for quarter in articles_per_quarter.keys():
            term_quarter_count[quarter] = term_quarter_count[quarter] / articles_per_quarter[quarter]

    return term_quarter_count

# Graphing

import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText

def add_correlation_box(series1, series2, ax):
    correlation = round(series1.corr(series2), 2)

    text_box = AnchoredText(f"corr = {correlation}", frameon=True, loc='lower right', pad=0.5)
    plt.setp(text_box.patch, facecolor='white', alpha=0.5)
    ax.add_artist(text_box)

import statsmodels.api as sm

def get_best_fit_values(df, column_name) -> list:
    """Get the line of best fit for a time graph
    
    column name is the name of the column of y values that you wish to 
    caluclate the line of best fit for"""

    num_quarters = len(df)
    # x var in this case is just time, so it increases linearly by units of 1
    X = range(0, num_quarters)
    X = sm.add_constant(X)
    Y = df[column_name]

    best_fit_model = sm.OLS(Y, X)
    best_fit_results = best_fit_model.fit()
    return best_fit_results.predict(X)

# Regression

import statsmodels.api as sm
import statsmodels.formula.api as smf
import math
from statsmodels.iolib.summary2 import summary_col
import pandas as pd

def add_quarter(data: pd.DataFrame) -> pd.DataFrame:
    """Takes a Dataframe with a year_quarter column and adds a quarter column"""
    data['quarter'] = data['year_quarter'].apply(lambda x: x[-1:])

    return data

def HAC_regression_w_controls(data: pd.DataFrame, formulas: list, model_names: list) -> pd.DataFrame:
    """Performs a heteroskedasticity and autocorrelation robust regression on a given dataset, 
    with various controls. Formulas should be R style strings that match data column names. 
    Returns the df of summary results"""

    max_lags = math.floor(len(data) ** (1/4))

    reg_results = []
    for formula in formulas: 
        reg_mod = smf.ols(formula=formula, data=data)
        reg_res = reg_mod.fit(cov_type='HAC', cov_kwds={'maxlags': max_lags}, use_t=True)
        # print(reg_results.summary())
        reg_results.append(reg_res)

    reg_summary_results = summary_col(reg_results, 
                                 regressor_order=reg_results[-1].params.index.tolist(), 
                                 stars=True, 
                                 float_format='%.2f',
                                 model_names=model_names)

    return reg_summary_results.tables[0]

