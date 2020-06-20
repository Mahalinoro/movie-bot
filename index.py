from flask import Flask, request, jsonify, render_template
import os
import dialogflow
import requests
import json
import pusher

app = Flask(__name__)

# initialize Pusher
pusher_client = pusher.Pusher(
  app_id='1022393',
  key='76961cbaed147db37fd5',
  secret='39a15f867e1dabb8e48f',
  cluster='ap2',
  ssl=True
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_movie_detail', methods=['POST'])
def get_movie_detail():
    data = request.get_json(silent=True)
    
    try:
        movie = data['queryResult']['parameters']['movie']
        api_key = '1235fc1b'
        
        movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
        movie_detail = json.loads(movie_detail)

        response =  """
            Title : {0} 
            Released: {1} 
            Actors: {2} 
            Plot: {3}
        """.format(movie_detail['Title'], movie_detail['Released'], movie_detail['Actors'], movie_detail['Plot'])
    except:
        response = "Could not get movie detail at the moment, please try again"
    
    reply = { "fulfillmentText": response }
    
    return jsonify(reply)

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    
    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        
        return response.query_result.fulfillment_text

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        socketId = request.form['socketId']
    except KeyError:
        socketId = ''
        
    message = request.form['message']
    project_id = 'movie-bot-dbfcdq'
    fulfillment_text = detect_intent_texts(project_id, "unique", message, 'en')
    response_text = { "message":  fulfillment_text }

    pusher_client.trigger(
        'movie_bot', 
        'new_message', 
        {
            'human_message': message, 
            'bot_message': fulfillment_text,
        },
        socketId
    )
                        
    return jsonify(response_text)
  
#  def explicit():
#     from google.cloud import storage

#     # Explicitly use service account credentials by specifying the private key
#     # file.
#     storage_client = storage.Client.from_service_account_json(
#         'movie-bot-dbfcdq-f3d6595b2774.json')

#     # Make an authenticated API request
#     buckets = list(storage_client.list_buckets())

# run Flask app
if __name__ == "__main__":
    app.run()
