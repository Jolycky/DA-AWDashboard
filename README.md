# DA-AWDashboard
## Adventure Works and IMDb Dashboard

This repository contains a Streamlit dashboard for data visualization using Adventure Works and IMDb datasets. The dashboard allows users to explore and analyze data through interactive visualizations. It also includes functionality for scraping data from the IMDb website. https://da-awdashboard.streamlit.app/

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [IMDB Scraping](#imdb-scraping)
- [License](#license)

## Project Overview
The goal of this project is to create an interactive data visualization dashboard using Streamlit. The dashboard provides insights into the Adventure Works dataset and IMDb data. It also demonstrates web scraping techniques to fetch and display the latest IMDb data.

## Features
- Interactive data visualizations for Adventure Works and IMDb datasets.
- Real-time data scraping from the IMDb website.
- User-friendly interface built with Streamlit.
- Multiple chart types including bar charts, line charts, and scatter plots.
- Filtering and sorting functionalities.

## Requirements
- Python 3.7 or higher
- Streamlit
- Pandas
- Requests
- BeautifulSoup (for web scraping)
- Plotly

## Installation
1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/da-awdashboard.streamlit.app.git
    cd da-awdashboard.streamlit.app
    ```

2. **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

2. **Access the dashboard:**
   Open your web browser and go to `http://localhost:8501`.

## Data Sources
### Adventure Works
Adventure Works is a sample database provided by Microsoft. It contains data for a fictional bicycle manufacturer, including sales, product inventory, and purchasing.

### IMDb
IMDb (Internet Movie Database) is an online database of information related to films, television programs, and video games. This dashboard includes functionalities to scrape the latest data from IMDb.

## IMDb Scraping
The dashboard includes a script to scrape IMDb data for the latest movies. The scraping functionality is implemented using the `requests` and `BeautifulSoup` libraries.

### How to Scrape IMDb Data
1. **Run the scraper script:**
    ```bash
    python scrape_imdb.py
    ```

2. **Update the dashboard:**
   The scraped data will be saved and used in the Streamlit dashboard.

##LICENSE
This project is licensed under the MIT License. See the LICENSE file for more details.



