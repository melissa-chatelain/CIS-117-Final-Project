# CIS117-FinalProject: Project Gutenberg Word Frequency  
Course: CIS 117 Python Final Project  
Authors: Kwame Puryear and Melissa Chatelain  
Date: May 12, 2026  

Overview:  
This program runs off of the Project Gutenberg library, it searches, downloads and scrapes what is inside to pull out the most common words (excluding predetermined filter words). It then stores those words into a database on SQLite in order to retrieve this on demand. 

Features:  
- Searches the Project Gutenberg Library to find the desired books.  
- Examines and shows the most common words in the chosen book.  
- Stores all of the previously searched books into a database with their most common words to get the data faster.  
- Uses Django to display the information and search for books in a more user friendly way.  

How To Use:   
- Upload the repository into codespace.  
- Once uploaded, using the terminal type in these commands one at a time:  
    - python3 -m pip install --upgrade pip  
    - cd gutenburg-final-project  
    - pip install -r requirements.txt  
    - python gutenberg_web.py runserver 0.0.0.0:8000  
- Once you type in the runserver command, there will be a popup asking to open in browser, click on that to launch the webpage. 
