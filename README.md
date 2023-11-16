# Steam Game Analysis and Visualization

## Introduction
This Flask application fetches and filters game data from the SteamSpy API based on user-defined tags. It then processes this data to filter games based on positive sentiment ratio and cost, and visualizes the similarities between these games using a network graph.

## Data Sources
- **SteamSpy API**: Used to fetch game data based on tags. SteamSpy provides various data points about games on the Steam platform. [SteamSpy API Documentation](https://steamspy.com/about)

## Access Techniques
- **API Requests**: Data is fetched using the `requests` library in Python to make calls to the SteamSpy API.
- **Web Scraping**: The `BeautifulSoup` library is used to scrape game descriptions from individual Steam game pages.

## Caching Strategy
- The application uses a caching mechanism to store API responses in JSON files. This reduces the number of API calls and speeds up data retrieval.
- Cache files are named using the tag and include a timestamp to identify the month and year of the cache.
- Cache validation checks the current month and year against the timestamp in the cache file. If they match, the cache is used; otherwise, new data is fetched.

## Data Summary
- Data includes game attributes such as name, price, positive and negative review counts, and a direct URL to the game's Steam page.
- Positive sentiment ratio is calculated as the number of positive reviews divided by the total number of reviews.
- Games are filtered based on a game tag, minimum positive sentiment ratio and a maximum cost threshold defined by the user.

## Data Structure
- The main data structure used is a dictionary with game IDs as keys and game information as values.
- NetworkX is used to create a graph structure where each node represents a game, and edges represent the similarity in positive sentiment ratio between games.

## Getting Started
This section guides you through setting up and running the Steam Game Analysis and Visualization Flask application on your local machine.

### Prerequisites
Before starting, ensure you have the following installed on your machine:
- Python (version 3.6 or later is recommended)
- pip (Python package installer)

### Installation

#### Step 1: Clone the Repository
Clone this repository to your local machine using the following command:
```bash
git clone https://github.com/mohammaw/507_final.git
cd 507_final 
```
#### Step 2: Set Up a Virtual Environment (Optional)
It's recommended to use a virtual environment for Python projects. To create and activate a virtual environment, run:
# Create a virtual environment
```bash
python -m venv venv
```

# Activate the virtual environment
# On Windows:
```bash
venv\Scripts\activate
```
# On MacOS/Linux:
```bash
source venv/bin/activate
```

#### Step 3: Install Dependencies
Install the necessary Python packages using pip:
```bash
pip install flask requests beautifulsoup4 matplotlib networkx
```

#### Step 4: Running Application
Start the Flask Server
Run the Flask application with the following command:
```bash
python app.py
```

#### Step 5: Accessiong the Web Interface:
Once the server is running, open your web browser and go to http://localhost:5000. Here, you can interact with the application's web interface.

## Acknowledgements
- Credits to SteamSpy API 

