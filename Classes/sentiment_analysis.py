import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from joblib import dump, load
import pandas as pd

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

# Define the callable function
def classify_sentiment(user_input):
    """Classify the sentiment of the user's input."""
    pipeline = load('sentiment_pipeline.joblib')
    sentiment = pipeline.predict([user_input])[0]
    return sentiment
