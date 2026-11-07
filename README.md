# **Battles**  

## Video Demo: 

## A Game of Guessing Dates  

For my CS50 project I made a simple web based game inspired by games such as [Chronophoto](https://www.chronophoto.app/game.html) which will show you some information about a famous battle or conflict that occurred in Europe and have you guess when it happened. It allows users to create an account and play rounds of the game.

## Getting the Data  
The data is sourced by scraping [Wikipedia](https://en.wikipedia.org/wiki/List_of_conflicts_in_Europe) at run time using an already prepared list of the links and corresponding years / time frames gathered from the link above. This was done using a Python script (not found in the repository) to scrape and store the links to the specific pages and their respective years.

## Frameworks used
This project uses a Flask frontend and is written in Python. An sqlite3 database is used to store all data including the user data and the links to all referenced battles sorted into different tables by year range. For the web scraping I used BeautifulSoup4 and requests to gather data from wikipedia, this all occurs in *lookup* in *helpers.py*. Bootstrap is used for the basic styling of the application in addition to */static/styles.css* which contains more custom styling for the application. 

## Overview of files
Being a Flask project all HTML templates are stored in */templates* in which all extend a standard *layout.html* and render specific aspects of the account creation process and the game play. The *app.py* file is the main project file and contains all the Flask routes. *helpers.py* contains three functions accessed by *app.py*, two of which are found in CS50s PSet 9 (*error* and *login_required*) the other *lookup* is the true heart of the project. It is responsible for getting the data needed to show the user from wikipedia and return it in the form of a dictionary. *data.db* is the SQLite3 database file used to store all the data used by the application. */static* simply contains the various .icos for the application and the css.

## Future improvements
This project isn't anywhere close to perfect and when I have some more time in the future I hope to try and improve it. Below is a list of key improvements I think implementing would improve the project
- A history of games: record each game played in an sql table and allow to user to view their history of games played.
- A leaderboard: the top users right now are shown on a leaderboard
- Additional gamemodes: more than one round is played at once or the game is played with other users
- Additional account management: a way to delete and modify an account