import requests
from bs4 import BeautifulSoup

# URL of the IMDb Top Picks page
url = "https://www.imdb.com/what-to-watch/top-picks/"

# Send a GET request to the URL
response = requests.get(url)
response.raise_for_status()  # Raise an error for bad status codes

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all movie containers in the Top Picks section
movie_containers = soup.find_all('a', class_='ipc-poster-card__title')

# Extract the titles and links
movies = []
for container in movie_containers:
    title = container.get_text(strip=True)
    link = "https://www.imdb.com" + container['href']
    movies.append((title, link))

# Print the movie titles and links
for title, link in movies:
    print(f"Title: {title}, Link: {link}")
