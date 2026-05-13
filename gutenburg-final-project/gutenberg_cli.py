"""
gutenburg-final-project
Project Gutenberg Book Analyzer - CLI Interface
Author: Kwame Puryear and Melissa Chatelain
Date: May 12, 2026
"""

from gutenberg_core import setup_database
from gutenberg_core import book_in_database
from gutenberg_core import get_word_frequencies
from gutenberg_core import fetch_book_from_web
from gutenberg_core import analyze_text
from gutenberg_core import search_gutenberg_by_title
from gutenberg_core import save_book_to_database


def display_results(title, word_frequencies):
    """Display the top 10 words in a nice format."""
    print("")
    print("==================================================")
    print("Top 10 Words in '" + title + "'")
    print("==================================================")

    rank = 1
    for pair in word_frequencies:
        word = pair[0]
        freq = pair[1]
        print(str(rank) + ". " + word + " - " + str(freq) + " times")
        rank = rank + 1

    print("==================================================")
    print("")


def search_book_cli(conn, title):
    """Search for book and display results in CLI."""

    # First check if the book is already in the database
    found = book_in_database(conn, title)

    if found:
        print("Found '" + title + "' in database")
        word_freqs = get_word_frequencies(conn, title)
        display_results(title, word_freqs)
        return

    # Book not in database, search Project Gutenberg
    print("'" + title + "' not in database")
    print("Searching Project Gutenberg...")

    try:
        results = search_gutenberg_by_title(title)
    except Exception as e:
        print("Error: " + str(e))
        return

    # If no results found, tell the user and stop
    if len(results) == 0:
        print("No books found for '" + title + "'")
        return

    # Show up to 5 results
    print("")
    print("Found " + str(len(results)) + " matches:")

    how_many_to_show = len(results)
    if how_many_to_show > 5:
        how_many_to_show = 5

    for i in range(how_many_to_show):
        book = results[i]
        book_title = book['title']

        # Build author string by hand
        author_string = ""
        for j in range(len(book['authors'])):
            if j > 0:
                author_string = author_string + ", "
            author_string = author_string + book['authors'][j]

        number = i + 1
        print(str(number) + ". " + book_title + " by " + author_string)

    # Let user pick a book
    choice = input("\nSelect book (1-5) or 0 to cancel: ")
    choice = choice.strip()

    # Validate the choice
    if not choice.isdigit():
        return

    choice_number = int(choice)

    if choice_number < 1:
        return

    if choice_number > how_many_to_show:
        return

    # Get the book the user selected
    selected_index = choice_number - 1
    selected = results[selected_index]
    selected_title = selected['title']
    selected_url = selected['url']

    # Fetch the book text from the web
    print("Fetching '" + selected_title + "'...")

    try:
        text = fetch_book_from_web(selected_url)
    except Exception as e:
        print("Error: " + str(e))
        return

    # Analyze the text
    print("Analyzing word frequencies...")
    word_freqs = analyze_text(text)

    # Save to database
    try:
        save_book_to_database(conn, selected_title, selected_url, word_freqs)
        print("Saved to database")
    except Exception as e:
        print("Error: " + str(e))
        return

    # Show the results
    display_results(selected_title, word_freqs)


def main():
    """Run the CLI application."""
    print("")
    print("==================================================")
    print("GUTENBURG-FINAL-PROJECT")
    print("PROJECT GUTENBERG BOOK ANALYZER - CLI")
    print("==================================================")

    conn = setup_database()

    try:
        while True:
            print("")
            print("1. Search for a book")
            print("2. Exit")

            choice = input("\nChoice: ")
            choice = choice.strip()

            if choice == '1':
                title = input("Book title: ")
                title = title.strip()
                if title != "":
                    search_book_cli(conn, title)

            elif choice == '2':
                print("")
                print("Goodbye!")
                break

    finally:
        conn.close()


if __name__ == "__main__":
    main()
