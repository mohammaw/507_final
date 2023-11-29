#Name: Mohammad Awad
# Final Project Steam Recommendation Program

'''
This assignment was completed with the help of the following resources:
ChatGPT: Error handling
Github Copilot: Code suggestions and snippets
'''

import subprocess
import sys


def install(package):
    '''
    Installs missing packages to run the program
    '''
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


required_packages = ['Flask',
                     'requests',
                     'matplotlib',
                     'networkx',
                     'beautifulsoup4']

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install(package)

from flask import Flask, render_template, request
import requests
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import os
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# Function to fetch game data by tag and cache the results


def get_games_by_tag(tag):
    '''
    Fetches game data by tag and caches the results
    '''
    cache_file = f"{tag}_cache.json"
    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            data = json.load(file)

        cache_month = data.get('cache_info', {}).get('cache_month')
        cache_year = data.get('cache_info', {}).get('cache_year')

        current_date = datetime.now()

        if (cache_month == current_date.month and
                cache_year == current_date.year):
            return data
        else:
            return fetch_and_cache_data(tag, cache_file)
    else:
        return fetch_and_cache_data(tag, cache_file)


def fetch_and_cache_data(tag, cache_file):
    '''
    Fetches game data by tag and caches the results
    '''
    url = f"https://steamspy.com/api.php?request=tag&tag={tag}"
    response = requests.get(url)
    data = response.json()
    current_date = datetime.now()
    cache_info = {
        'cache_month': current_date.month,
        'cache_year': current_date.year
    }
    data['cache_info'] = cache_info

    with open(cache_file, "w") as file:
        json.dump(data, file)

    return data


def scrape_game_description(url):
    '''
    Scrapes the game description from the Steam store page
    '''
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        description_tag = soup.find('div', class_='game_description_snippet')
        if description_tag:
            return description_tag.text.strip()
        else:
            return "Description not available"
    except Exception as e:
        print(f"Error occurred while scraping: {e}")
        return "Description not available"


# Function to filter games by positive sentiment ratio and cost
def filter_games(games, min_positive_sentiment, max_cost):
    '''
    Filters games by positive sentiment ratio and cost

    Returns a list of the top 10 games
    '''
    preliminary_filtered_games = []
    for appid, game_data in games.items():
        if ("positive" in game_data and
                "negative" in game_data and
                "price" in game_data):
            positive = int(game_data["positive"])
            negative = int(game_data["negative"])
            price_in_cents = int(game_data["price"])
            price_in_dollars = price_in_cents / 100
            developer = game_data["developer"]

            if (positive + negative) == 0:
                sentiment_ratio = 0
            else:
                sentiment_ratio = positive / (positive + negative)
                sentiment_ratio = round(sentiment_ratio, 2)

            if (sentiment_ratio >= min_positive_sentiment and
                    (price_in_dollars <= max_cost or
                        price_in_dollars == 0)):
                preliminary_filtered_games.append({
                    "appid": appid,
                    "name": game_data.get("name", "N/A"),
                    "positive_sentiment_ratio": sentiment_ratio,
                    "price_in_dollars": price_in_dollars,
                    "developer": developer,
                    "steam_url": f"https://store.steampowered.com/app/{appid}",
                })

    top_games = preliminary_filtered_games[:10]
    for game in top_games:
        game['description'] = scrape_game_description(game['steam_url'])

    return top_games


def calculate_similarity(game1, game2):
    '''
    Calculates the similarity between two games based on the developer
    '''
    if game1['developer'] == game2['developer']:
        return 1
    else:
        return 10


def create_similarity_graph(games):
    '''
    Creates a similarity graph based on the developer of the games
    '''
    G = nx.Graph()
    # Add nodes for each game
    for game in games:
        G.add_node(game['appid'],
                    name=game['name'],
                        developer=game['developer'])

    # Add edges only between games with the same developer
    for i in range(len(games)):
        for j in range(i + 1, len(games)):
            if games[i]['developer'] == games[j]['developer']:
                G.add_edge(games[i]['appid'], games[j]['appid'])

    return G


def check_developer_similarity(games):
    '''
    Checks the similarity between games based on the developer
    '''
    for i in range(len(games)):
        for j in range(i + 1, len(games)):
            similarity_weight = calculate_similarity(games[i], games[j])
            if similarity_weight == 1:
                print("Games '" + games[i]['name'] + "' and '"
                      + games[j]['name'] +
                      "' have the same developer.")
            else:
                print("Games '" + games[i]['name'] + "' and '"
                      + games[j]['name'] +
                      "' have different developers.")


def visualize_similarity_graph(G):
    '''
    Creates a visualization of the similarity graph
    '''
    pos = nx.spring_layout(G, k=0.5, iterations=20)
    labels = nx.get_node_attributes(G, 'name')

    plt.figure(figsize=(12, 12))
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    nx.draw_networkx_edges(G, pos, width=2.0, edge_color='black')

    plt.title("Game Similarity Graph - Same Developer Connections")
    plt.savefig('static/game_similarity_graph.png')
    plt.close()
    return 'static/game_similarity_graph.png'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    tag = request.form['tag']
    min_positive_sentiment = request.form['min_positive_sentiment']
    max_cost = float(request.form['max_cost'])

    try:
        if isinstance(min_positive_sentiment, str):
            min_positive_sentiment = min_positive_sentiment.strip('%')
        min_positive_sentiment = float(min_positive_sentiment)
    except ValueError:
        pass

    games_by_tag = get_games_by_tag(tag)
    filtered_args = (games_by_tag, min_positive_sentiment, max_cost)
    filtered_games = filter_games(*filtered_args)

    if filtered_games:
        similarity_graph = create_similarity_graph(filtered_games)
        graph_image_path = visualize_similarity_graph(similarity_graph)
        graph_image_url = '/' + graph_image_path
    else:
        graph_image_url = None

    return render_template('results.html', games=filtered_games, graph_image_url=graph_image_url)


if __name__ == '__main__':
    app.run(debug=True)
