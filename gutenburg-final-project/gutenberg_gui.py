"""
Project Gutenberg Book Analyzer - Simple Tkinter GUI
Author: Kwame Puryear
Date: May 11, 2026
"""

from tkinter import Tk, Label, Entry, Button, Text, END, W, WORD, messagebox
from gutenberg_core import *


def click():
    """Handle SUBMIT button - search database or web, display top 10 words."""
    title = text_entry.get().strip()
    
    if not title:
        messagebox.showwarning("Input Required", "Please enter a book title")
        return
    
    output.delete(1.0, END)
    output.insert(END, "Searching...\n")
    window.update()
    
    try:
        conn = setup_database()
        
        # Check database first
        if book_in_database(conn, title):
            output.delete(1.0, END)
            output.insert(END, f"Found '{title}' in database\n\n")
            word_freqs = get_word_frequencies(conn, title)
        
        else:
            # Search Project Gutenberg
            output.delete(1.0, END)
            output.insert(END, f"Searching Project Gutenberg for '{title}'...\n")
            window.update()
            
            results = search_gutenberg_by_title(title)
            
            if not results:
                output.delete(1.0, END)
                output.insert(END, f"No books found for '{title}'")
                conn.close()
                return
            
            # Auto-select best match (first result, sorted by popularity)
            selected = results[0]
            
            output.delete(1.0, END)
            output.insert(END, f"Fetching '{selected['title']}'...\n")
            window.update()
            
            text = fetch_book_from_web(selected['url'])
            
            output.insert(END, "Analyzing word frequencies...\n")
            window.update()
            
            word_freqs = analyze_text(text)
            save_book_to_database(conn, selected['title'], selected['url'], word_freqs)
            title = selected['title']
        
        # Display results
        output.delete(1.0, END)
        result = f"Top 10 Words in '{title}'\n"
        result += "=" * 40 + "\n\n"
        for i, (word, freq) in enumerate(word_freqs, 1):
            result += f"{i:2}. {word:20} {freq:5} times\n"
        output.insert(END, result)
        
        conn.close()
    
    except Exception as e:
        output.delete(1.0, END)
        output.insert(END, f"Error: {str(e)}")


# Build window (matches lesson style)
window = Tk()
window.title("Project Gutenberg Book Analyzer")

Label(window, text="Enter book title: ").grid(row=1, column=0, sticky=W)

text_entry = Entry(window, width=40)
text_entry.grid(row=2, column=0, sticky=W)

Button(window, text="SUBMIT", width=6, command=click).grid(row=3, column=0, sticky=W)

output = Text(window, width=60, height=15, wrap=WORD)
output.grid(row=5, column=0, columnspan=2, sticky=W)

window.mainloop()
