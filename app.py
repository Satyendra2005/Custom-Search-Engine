from flask import Flask, render_template, request, jsonify
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import requests

app = Flask(__name__)

GOOGLE_API_KEY = 'AIzaSyB2RL9qjEXQ1oI8Mql2QSSx55plasydzGg'
SEARCH_ENGINE_ID = '36f5ea86e46194656'

user_data = {
    'user1': {'interactions': ['item1', 'item2'], 'preferences': [0.8, 0.2]},
    'user2': {'interactions': ['item2', 'item3'], 'preferences': [0.5, 0.5]},
}
item_data = {
    'item1': {'features': [1, 0, 0]},
    'item2': {'features': [0, 1, 0]},
    'item3': {'features': [0, 0, 1]},
}
context_data = {
    'user1': {'location': 'home', 'time': 'morning'},
    'user2': {'location': 'work', 'time': 'afternoon'},
}
interaction_data = {
    'user1': {'item1': 1, 'item2': 0},
    'user2': {'item2': 1, 'item3': 1},
}

def generate_context_embeddings(context_data):
    embeddings = {}
    for user, context in context_data.items():
        embeddings[user] = np.random.rand(3)
    return embeddings

def preprocess_data(user_data, item_data, context_data):
    preprocessed_user_data = normalize(np.array([user['preferences'] for user in user_data.values()]))
    preprocessed_item_data = normalize(np.array([item['features'] for item in item_data.values()]))
    preprocessed_context_data = normalize(np.array([np.random.rand(3) for _ in context_data.values()]))
    return preprocessed_user_data, preprocessed_item_data, preprocessed_context_data

def collaborative_filtering(user_data, interaction_data):
    recommendations = {}
    for user, interactions in interaction_data.items():
        user_vector = np.array(list(interactions.values()))
        sim_scores = {}
        for other_user, other_interactions in interaction_data.items():
            if user != other_user:
                other_vector = np.array(list(other_interactions.values()))
                sim_scores[other_user] = cosine_similarity(user_vector.reshape(1, -1), other_vector.reshape(1, -1))[0][0]
        recommendations[user] = sim_scores
    return recommendations

def content_based_filtering(user_data, item_data):
    recommendations = {}
    for user, details in user_data.items():
        user_preferences = np.array(details['preferences'])
        item_features = np.array([item_data[item]['features'] for item in item_data])
        sim_scores = cosine_similarity(user_preferences.reshape(1, -1), item_features)[0]
        recommendations[user] = {item: sim_scores[idx] for idx, item in enumerate(item_data)}
    return recommendations

def knowledge_based_filtering(user_data, item_data):
    recommendations = {user: {item: np.random.rand() for item in item_data} for user in user_data}
    return recommendations

def hybrid_filtering(collab_recs, content_recs, knowledge_recs):
    combined_recommendations = {}
    for user in collab_recs.keys():
        combined_scores = {}
        for item in content_recs[user].keys():
            combined_scores[item] = (
                0.4 * collab_recs[user].get(item, 0) + 
                0.4 * content_recs[user].get(item, 0) + 
                0.2 * knowledge_recs[user].get(item, 0)
            )
        combined_recommendations[user] = combined_scores
    return combined_recommendations

def personalize_recommendations(combined_recommendations, context_embeddings):
    personalized_recommendations = {}
    for user, scores in combined_recommendations.items():
        context_score = context_embeddings[user].mean()
        personalized_recommendations[user] = {item: score * context_score for item, score in scores.items()}
    return personalized_recommendations

@app.route('/')
def home():
    return render_template('index.html') 

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if query:
        preprocessed_user_data, preprocessed_item_data, preprocessed_context_data = preprocess_data(user_data, item_data, context_data)
        context_embeddings = generate_context_embeddings(context_data)
        collaborative_recommendations = collaborative_filtering(user_data, interaction_data)
        content_based_recommendations = content_based_filtering(user_data, item_data)
        knowledge_based_recommendations = knowledge_based_filtering(user_data, item_data)
        combined_recommendations = hybrid_filtering(collaborative_recommendations, content_based_recommendations, knowledge_based_recommendations)
        personalized_recommendations = personalize_recommendations(combined_recommendations, context_embeddings)

        search_results = search_google(query, GOOGLE_API_KEY, SEARCH_ENGINE_ID)

        results = []
        for user, recs in personalized_recommendations.items():
            user_results = {'user': user, 'results': []}
            for item in search_results.get('items', []):
                title = item['title']
                link = item['link']
                score = recs.get(title, 'N/A')
                user_results['results'].append({'title': title, 'link': link, 'score': score})
            results.append(user_results)
        
        return jsonify(results)
    
    return jsonify({'error': 'No query provided'})

def search_google(query, api_key, cse_id):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query
    }
    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    app.run(debug=True)
