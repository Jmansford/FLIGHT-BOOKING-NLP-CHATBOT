from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from joblib import dump, load
import pandas as pd
from Classes.responses import get_response

# Load the new training dataset
data = pd.read_csv('Resources/large_sentiment_training_dataset.csv')
responses = data["Response"].values
sentiments = data["Sentiment"].values

# Define the pipeline
pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(max_features=3000, sublinear_tf=True, use_idf=True, ngram_range=(1, 2))),
    ('classifier', LogisticRegression(C=1.0, max_iter=200))  
])

# Cross-validation for evaluation
scores = cross_val_score(pipeline, responses, sentiments, cv=5)

# Train the model
pipeline.fit(responses, sentiments)

# Save the model for reuse
dump(pipeline, 'sentiment_pipeline.joblib')

def classify_sentiment(user_input, name):
    pipeline = load('sentiment_pipeline.joblib')
    sentiment = pipeline.predict([user_input])[0]
    if sentiment == "positive":
        print(get_response("positive_feelings", name=name))
    elif sentiment == "negative":
        print(get_response("negative_feelings", name=name))
    else:
        print(get_response("neutral_feelings", name=name))

