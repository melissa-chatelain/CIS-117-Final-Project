"""
gutenburg-final-project
Project Gutenberg Book Analyzer - Core Logic
Author: Kwame Puryear and Melissa Chatelain
Date: May 12, 2026

Core business logic for analyzing Project Gutenberg books.
Can be used with CLI, GUI, or web interfaces.
"""

import sqlite3
import re
import json
from urllib.request import urlopen


def setup_database(db_path='books.db'):
    """Create database and tables if they don't exist."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS books (
        title TEXT PRIMARY KEY,
        url TEXT
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS words (
        book_title TEXT,
        word TEXT,
        frequency INTEGER
    )""")

    conn.commit()
    return conn


def book_in_database(conn, title):
    """Check if book exists in database."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM books WHERE title = ?", (title,))
    row = cur.fetchone()
    count = row[0]
    if count > 0:
        return True
    else:
        return False


def get_word_frequencies(conn, title):
    """Get top 10 words from database."""
    cur = conn.cursor()
    cur.execute("""SELECT word, frequency
                   FROM words
                   WHERE book_title = ?
                   ORDER BY frequency DESC
                   LIMIT 10""", (title,))
    results = cur.fetchall()
    return results


def fetch_book_from_web(url):
    """Fetch book text from Project Gutenberg."""
    try:
        response = urlopen(url)
        raw_data = response.read()
        text = raw_data.decode('utf-8')
        return text
    except Exception as e:
        raise Exception("Error fetching book: " + str(e))


def analyze_text(text):
    """
    Count word frequencies and return top 10.

    Filters words that don't add meaning to a text, such as articles, prepositions,
    and simular. This list comes from "NLTK's list of english stopwords"
    <https://gist.github.com/sebleier/554280>
    """
    filter_words = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
        "you", "your", "yours", "yourself", "yourselves",
        "he", "him", "his", "himself", "she", "her", "hers", "herself",
        "it", "its", "itself",
        "they", "them", "their", "theirs", "themselves",
        "what", "which", "who", "whom",
        "this", "that", "these", "those",
        "am", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "having",
        "do", "does", "did", "doing",
        "a", "an", "the", "and", "but", "if", "or",
        "because", "as", "until", "while",
        "of", "at", "by", "for", "with", "about", "against",
        "between", "into", "through", "during", "before", "after",
        "above", "below", "to", "from", "up", "down",
        "in", "out", "on", "off", "over", "under",
        "again", "further", "then", "once",
        "here", "there", "when", "where", "why", "how",
        "all", "any", "both", "each", "few", "more", "most",
        "other", "some", "such",
        "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very",
        "s", "t", "can", "will", "just", "don", "should", "now"
    }

    """ Regular Expression for words """
    lowercase_text = text.lower()
    words = re.findall(r'\b[a-z]+\b', lowercase_text)

    # Count how many times each word appears
    word_count = {}
    for word in words:
        if word in filter_words:
            continue
        if len(word) <= 2:
            continue
        if word in word_count:
            word_count[word] = word_count[word] + 1
        else:
            word_count[word] = 1

    # Sort the words by frequency from highest to lowest
    word_list = []
    for word in word_count:
        freq = word_count[word]
        pair = (word, freq)
        word_list.append(pair)

    # Bubble sort by frequency (descending)
    for i in range(len(word_list)):
        for j in range(len(word_list) - 1):
            freq_a = word_list[j][1]
            freq_b = word_list[j + 1][1]
            if freq_b > freq_a:
                temp = word_list[j]
                word_list[j] = word_list[j + 1]
                word_list[j + 1] = temp

    # Return only the top 10
    top_ten = word_list[:10]
    return top_ten


def search_gutenberg_by_title(title):
    """
    Search Project Gutenberg using Gutendex API.
    Returns list of matching books with their download URLs.
    """
    try:
        search_term = title.replace(' ', '%20')
        url = "https://gutendex.com/books?search=" + search_term

        response = urlopen(url)
        raw_data = response.read()
        data_string = raw_data.decode('utf-8')
        results = json.loads(data_string)

        books = []
        for book in results['results']:
            # Try to get the plain text URL
            formats = book['formats']
            text_url = None

            if 'text/plain; charset=utf-8' in formats:
                text_url = formats['text/plain; charset=utf-8']
            elif 'text/plain' in formats:
                text_url = formats['text/plain']

            # Only add this book if we found a text URL
            if text_url is not None:
                # Get the author names
                author_names = []
                for author in book['authors']:
                    name = author['name']
                    author_names.append(name)

                book_info = {}
                book_info['title'] = book['title']
                book_info['url'] = text_url
                book_info['id'] = book['id']
                book_info['authors'] = author_names
                book_info['download_count'] = book['download_count']

                books.append(book_info)

        return books

    except Exception as e:
        raise Exception("Error searching Gutenberg: " + str(e))


def save_book_to_database(conn, title, url, word_frequencies):
    """Save book and word frequencies to database."""
    try:
        cur = conn.cursor()

        cur.execute("INSERT OR REPLACE INTO books (title, url) VALUES (?, ?)",
                    (title, url))

        cur.execute("DELETE FROM words WHERE book_title = ?", (title,))

        for pair in word_frequencies:
            word = pair[0]
            freq = pair[1]
            cur.execute("INSERT INTO words (book_title, word, frequency) VALUES (?, ?, ?)",
                        (title, word, freq))

        conn.commit()

    except Exception as e:
        raise Exception("Error saving to database: " + str(e))
