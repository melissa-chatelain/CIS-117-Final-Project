"""
gutenburg-final-project
Project Gutenberg Book Analyzer - Django Web Interface
Author: Kwame Puryear and Melissa Chatelain
Date: May 12, 2026

Single-file Django app based on the template from:
https://minimalistdjango.com/snippets/2024-09-01-django-onefile-project-template/

Run with: python gutenberg_web.py runserver
"""

import sys

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.urls import path
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect

from gutenberg_core import setup_database
from gutenberg_core import book_in_database
from gutenberg_core import get_word_frequencies
from gutenberg_core import fetch_book_from_web
from gutenberg_core import analyze_text
from gutenberg_core import search_gutenberg_by_title
from gutenberg_core import save_book_to_database


settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    SECRET_KEY="change-this-to-something-secret",
    ALLOWED_HOSTS=["*"],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["templates"],
        },
    ],
)


def index(request):
    """Show the main search page."""
    context = {}
    return TemplateResponse(request, "index.html", context)


def search(request):
    """Search for a book by title."""

    # Get the title from the form
    title = request.POST.get("title", "")
    title = title.strip()

    # If no title was entered, go back to the main page
    if title == "":
        return HttpResponseRedirect("/")

    # Open the database
    conn = setup_database()

    # Check if the book is already in the database
    found = book_in_database(conn, title)

    if found:
        # Get the word frequencies from the database
        word_freqs = get_word_frequencies(conn, title)
        conn.close()

        # Build a list of rank/word/freq for the template
        ranked_words = []
        rank = 1
        for pair in word_freqs:
            word = pair[0]
            freq = pair[1]
            entry = {}
            entry["rank"] = rank
            entry["word"] = word
            entry["frequency"] = freq
            ranked_words.append(entry)
            rank = rank + 1

        context = {}
        context["title"] = title
        context["word_frequencies"] = ranked_words
        context["from_database"] = True
        return TemplateResponse(request, "frequencies.html", context)

    # Book not in database, search Project Gutenberg
    try:
        results = search_gutenberg_by_title(title)
    except Exception as e:
        conn.close()
        context = {}
        context["error"] = "Error searching Gutenberg: " + str(e)
        context["title"] = title
        return TemplateResponse(request, "search_results.html", context)

    conn.close()

    # If no results found, tell the user
    if len(results) == 0:
        context = {}
        context["title"] = title
        context["no_results"] = True
        return TemplateResponse(request, "search_results.html", context)

    # Show up to 5 results
    books_to_show = []
    how_many = len(results)
    if how_many > 5:
        how_many = 5

    for i in range(how_many):
        book = results[i]

        # Build author string by hand
        author_string = ""
        for j in range(len(book["authors"])):
            if j > 0:
                author_string = author_string + ", "
            author_string = author_string + book["authors"][j]

        entry = {}
        entry["title"] = book["title"]
        entry["url"] = book["url"]
        entry["authors"] = author_string
        entry["number"] = i + 1
        books_to_show.append(entry)

    context = {}
    context["title"] = title
    context["books"] = books_to_show
    return TemplateResponse(request, "search_results.html", context)


def analyze(request):
    """Fetch a book from the web, analyze it, and save it."""

    # Get the title and URL from the form
    book_title = request.POST.get("book_title", "")
    book_url = request.POST.get("book_url", "")

    # If either is missing, go back to the main page
    if book_title == "" or book_url == "":
        return HttpResponseRedirect("/")

    # Fetch the book text from the web
    try:
        text = fetch_book_from_web(book_url)
    except Exception as e:
        context = {}
        context["error"] = "Error fetching book: " + str(e)
        return TemplateResponse(request, "frequencies.html", context)

    # Analyze the text
    word_freqs = analyze_text(text)

    # Save to database
    conn = setup_database()
    try:
        save_book_to_database(conn, book_title, book_url, word_freqs)
    except Exception as e:
        conn.close()
        context = {}
        context["error"] = "Error saving to database: " + str(e)
        return TemplateResponse(request, "frequencies.html", context)

    conn.close()

    # Build a list of rank/word/freq for the template
    ranked_words = []
    rank = 1
    for pair in word_freqs:
        word = pair[0]
        freq = pair[1]
        entry = {}
        entry["rank"] = rank
        entry["word"] = word
        entry["frequency"] = freq
        ranked_words.append(entry)
        rank = rank + 1

    context = {}
    context["title"] = book_title
    context["word_frequencies"] = ranked_words
    context["from_database"] = False
    return TemplateResponse(request, "frequencies.html", context)


urlpatterns = [
    path("", index),
    path("search/", search),
    path("analyze/", analyze),
]

application = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
