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
    cache_file = f"{tag}_cache.json"
    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            data = json.load(file)

        cache_month = data.get('cache_info', {}).get('cache_month')
        cache_year = data.get('cache_info', {}).get('cache_year')

        current_date = datetime.now()

        if cache_month == current_date.month and cache_year == current_date.year:
            return data
        else:
            return fetch_and_cache_data(tag, cache_file)
    else:
        return fetch_and_cache_data(tag, cache_file)

def fetch_and_cache_data(tag, cache_file):
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
    preliminary_filtered_games = []
    for appid, game_data in games.items():
        if "positive" in game_data and "negative" in game_data and "price" in game_data:
            positive = int(game_data["positive"])
            negative = int(game_data["negative"])
            price_in_cents = int(game_data["price"])
            price_in_dollars = price_in_cents / 100

            if (positive + negative) == 0:
                sentiment_ratio = 0
            else:
                sentiment_ratio = positive / (positive + negative)
                sentiment_ratio = round(sentiment_ratio, 2)

            if sentiment_ratio >= min_positive_sentiment and (price_in_dollars <= max_cost or price_in_dollars == 0):
                preliminary_filtered_games.append({
                    "appid": appid,
                    "name": game_data.get("name", "N/A"),
                    "positive_sentiment_ratio": sentiment_ratio,
                    "price_in_dollars": price_in_dollars,
                    "steam_url": f"https://store.steampowered.com/app/{appid}",
                })

    top_games = preliminary_filtered_games[:10]
    for game in top_games:
        game['description'] = scrape_game_description(game['steam_url'])

    return top_games

def create_similarity_graph(games):
    G = nx.Graph()
    for game in games:
        G.add_node(game['appid'], name=game['name'])
    for game1 in games:
        for game2 in games:
            if game1['appid'] != game2['appid']:
                similarity = abs(game1['positive_sentiment_ratio'] - game2['positive_sentiment_ratio'])
                G.add_edge(game1['appid'], game2['appid'], weight=similarity)

    return G

def visualize_similarity_graph(G):
    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'name')
    weights = [G[u][v]['weight'] * 10 for u, v in G.edges]

    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=2000, node_color='lightblue', font_size=8, font_color='black', width=weights, edge_color='gray')
    plt.title("Game Similarity Graph")
    plt.show()

    static_dir = "static"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    graph_image_path = os.path.join(static_dir, "game_similarity_graph.png")
    plt.savefig(graph_image_path)
    plt.close()
    return graph_image_path

# Route to display the input form
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Route to handle form submission and display results
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

    # Fetch and filter games
    games_by_tag = get_games_by_tag(tag)
    filtered_games = filter_games(games_by_tag, min_positive_sentiment, max_cost)

    # Check if there are games to process and create and visualize the similarity graph
    if filtered_games:
        similarity_graph = create_similarity_graph(filtered_games)
        graph_image_path = visualize_similarity_graph(similarity_graph)
        graph_image_url = '/' + graph_image_path
    else:
        graph_image_url = None

    return render_template('results.html', games=filtered_games, graph_image_url=graph_image_url)

if __name__ == '__main__':
    app.run(debug=True)
