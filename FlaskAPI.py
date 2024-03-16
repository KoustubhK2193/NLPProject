from flask import Flask, request, jsonify
import requests
import re
from bs4 import BeautifulSoup
import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

def scrape_text(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all text elements on the page
        text_elements = soup.find_all(string=True)
        # Extract and concatenate the text from each element
        text = ' '.join(element.strip() for element in text_elements if element.strip())
        return text
    else:
        print("Failed to retrieve the webpage.")
        return None

def remove_enclosed_text(input_string):
    # Define a regular expression pattern to match text enclosed in < and >
    pattern = r'<[^>]*>'
    # Use re.sub() to replace matched patterns with an empty string
    new_string = re.sub(pattern, '', input_string)
    return new_string

def tokenize_text(text):
    # Tokenize the text into words
    tokens = word_tokenize(text)
    return tokens

def remove_html_tokens(tokens):
    # Define a regular expression pattern to match HTML tags
    html_tag_pattern = r'<[^>]+>'
    # Remove HTML tags and tokens containing '<' or '>'
    clean_tokens = [token for token in tokens if not re.match(html_tag_pattern, token)]
    return clean_tokens

def remove_stopwords_and_punctuation(text):
    # Tokenize the text into words
    words = nltk.word_tokenize(text)
    # Get the set of stopwords
    stop_words = set(stopwords.words('english'))
    # Remove stopwords and punctuation
    clean_words = [word for word in words if word.lower() not in stop_words and word not in string.punctuation]
    # Join the clean words back into a single string
    clean_text = ' '.join(clean_words)
    return clean_text

def count_words_frequency(tokens):
    words_to_search = ["download", "now", "click", "here", "visit", "add", "to", "cart"]
    # Initialize a dictionary to store the frequency of each word
    word_frequency = {word: 0 for word in words_to_search}
    # Iterate through the tokens
    for token in tokens:
        # Check if the token is one of the words to search for
        if token.lower() in word_frequency:
            # Increment the frequency count for the token
            word_frequency[token.lower()] += 1
    return word_frequency

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get the URL from the request data
    url = request.json.get('url')
    # Scrape text from the URL
    text = scrape_text(url)
    if text:
        # Remove enclosed text
        text = remove_enclosed_text(text)
        # Remove stopwords and punctuation
        text = remove_stopwords_and_punctuation(text)
        # Tokenize the cleaned text
        tokens = tokenize_text(text)
        # Remove HTML tokens
        tokens = remove_html_tokens(tokens)
        # Count word frequency
        word_frequency = count_words_frequency(tokens)
        count = 0
        for word, frequency in word_frequency:
          count += frequency
        if count/len(tokens)<0.0003:
          return jsonify("Safe Site")
        else:
          return jsonify("Not Safe")
    else:
        return jsonify({'error': 'Failed to retrieve the webpage.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
