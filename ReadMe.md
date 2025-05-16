# Advanced Chatbot System with Natural Language Processing

## Project Overview
This project implements an intelligent chatbot system that uses multiple advanced Natural Language Processing (NLP) techniques to understand user queries, determine intent, analyse sentiment, and facilitate flight bookings. The system combines rule-based pattern matching with machine learning approaches to provide a responsive and context-aware conversational experience.

## Key Features
- **Intent Classification**: Identifies user intent through keyword matching, bigram and trigram pattern recognition
- **Question-Answering System**: Uses TF-IDF vectorisation and cosine similarity to match user queries with predefined Q&A pairs
- **Sentiment Analysis**: Employs a Logistic Regression model trained on a large dataset to classify sentiment in user messages
- **Flight Booking System**: Manages a complete booking flow with database integration and fuzzy text matching
- **Contextual Responses**: Generates appropriate responses based on identified intent and conversation context
- **Database Integration**: Stores and retrieves booking information using SQLite

## Technical Implementation
### Natural Language Processing Techniques
- **Text Preprocessing**: Tokenisation, lemmatisation, and stop word removal
- **Fuzzy Matching**: Uses edit distance metrics to handle spelling mistakes in location names
- **Part-of-Speech Tagging**: Identifies word types to extract relevant information from queries
- **TF-IDF Vectorisation**: Converts text into numerical vectors for similarity comparisons
- **N-gram Analysis**: Examines word patterns using unigrams, bigrams, and trigrams

### Machine Learning Approaches
- **Logistic Regression**: Powers the sentiment analysis pipeline
- **Pipeline Architecture**: Combines vectorisation and classification steps
- **Cross-Validation**: Ensures model reliability through k-fold evaluation

### System Architecture
The system is organised into modular Python classes that handle specific functionality:
- Intent matching and question answering
- Sentiment analysis
- Booking flow management
- Response generation
- Database operations
- Date parsing and entity recognition

## Usage
The chatbot provides a natural conversation interface where users can:
- Ask general questions
- Book flights between supported cities
- Receive personalised responses based on sentiment
- View and cancel existing bookings
