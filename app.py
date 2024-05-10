# app.py
from flask import Flask, render_template, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from langchain_community.llms import Ollama
from sqlalchemy import desc
from sqlalchemy import func
import requests
import os
import uuid
import json
from llm import myllm
from llm import myvisionmodel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

# Define the ChatHistory model
class ChatHistory(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    conversation_history = db.Column(db.Text)

# Initialize conversation history
conversation_history = []
session_id = ''
@app.route('/', methods=['GET', 'POST'])
def index():
    global conversation_history
    global session_id

    # When the home page is loaded
    if request.method == 'GET':
        conversation_history = []
        # Generate a unique session ID for each session or each time page is loaded
        session_id = str(uuid.uuid4())
        get_or_create_session(session_id)
        user_messages = chat_history()
        print(session_id + " I am get request session ID")
        return render_template('index.html', conversation_history=conversation_history, session_id=session_id, user_messages = user_messages)
    
    # If users asks Questions
    if request.method == 'POST':
        user_input = request.form['user_input']
        session_id = request.form['session_id']
       
       
        # Initialize file_path as None
        file_path = None

        # Fetch the conversation history from the database
        conversation_history = get_or_create_session(session_id)

         # Handle file upload
        if 'file' in request.files:
            uploaded_file = request.files['file']
            if uploaded_file.filename != '':
            # Save the file to the desired folder
                #file_path = os.path.join('Static', 'UserFiles', uploaded_file.filename)
                #file_path = os.path.join(r'Static\UserFiles', uploaded_file.filename)
                file_path = os.path.join('Static', 'UserFiles', uploaded_file.filename.replace('\\', '\\\\'))

                uploaded_file.save(file_path)

        # Append the user input to the conversation history
        conversation_history.append({'user': user_input})

        # Append the file path to the conversation history
        conversation_history.append({'file': file_path})
        
        # Call your LLM model API to get the response
        if file_path is not None:
            response = myvisionmodel(user_input,file_path)
        else:    
            response = myllm(user_input)
        
        # Append bot response to the conversation history
        conversation_history.append({'bot': response})

        # Update the conversation history in the database
        update_session(session_id, conversation_history)

        #load chat history table
        user_messages = chat_history()

        # Use for testing the session, user input and bot response
        print(session_id)
        print(user_input)
        print (response)
        print(file_path)
        return render_template('index.html', conversation_history=conversation_history, session_id=session_id, user_messages=user_messages)
    else:
        # If it's a GET request, initialize conversation history
        conversation_history = []
        return render_template('index.html', conversation_history=conversation_history, session_id=session_id)
    
#route to load specfic chat
@app.route("/load/<id>", methods=['GET', 'POST'])
def loadChat(id):
    if request.method == 'GET':
        session_id = id
        # Assuming get_or_create_session is defined elsewhere
        conversation_history = get_or_create_session(session_id)
        #load chat history table
        user_messages = chat_history()
        print(f'I am clicked from table')
        return render_template('index.html', conversation_history=conversation_history, session_id=session_id, user_messages=user_messages)
    else:
        # Handle GET request here if needed
        pass

    
# Route to delete all chat history
@app.route('/delete_all', methods=['DELETE','GET'])
def delete_all():
    try:
        # Delete all rows from the chat_history table
        db.session.query(ChatHistory).delete()
        db.session.commit()
        return jsonify({'message': 'All chat history deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Database Queries
   
def get_last_session_id():
    # Query the last row in the ChatHistory table
    last_session = ChatHistory.query.order_by(ChatHistory.id.desc()).first()
    if last_session:
        # If a row exists, return its ID
        return last_session.id
    
def get_or_create_session(session_id):
    # Check if the session ID already exists in the database
    existing_session = ChatHistory.query.filter_by(id=session_id).first()
    if existing_session:
        # If session exists, return the conversation history
        return json.loads(existing_session.conversation_history)
    else:
        # If session does not exist, create a new entry with an empty conversation history
        new_entry = ChatHistory(id=session_id, conversation_history=json.dumps([]))
        db.session.add(new_entry)
        db.session.commit()
        return []
    
def update_session(session_id, conversation_history):
    # Update the conversation history in the database
    session = ChatHistory.query.filter_by(id=session_id).first()
    session.conversation_history = json.dumps(conversation_history)
    db.session.commit()    


def chat_history():
    # Fetch only valid chat history entries from the database where session ID is not null
    valid_chat_history = ChatHistory.query.filter(
        ChatHistory.id.isnot(None),
        ChatHistory.conversation_history != '[]'
    ).all()
    # Extract user messages along with their IDs
    user_messages = []
    for entry in valid_chat_history:
        conversation = json.loads(entry.conversation_history)
        if conversation:
            first_user_message = next((msg["user"] for msg in conversation if "user" in msg), None)
            if first_user_message:
                user_messages.append({"id": entry.id, "user": first_user_message})
    return user_messages

if __name__ == '__main__':
    app.run(debug=True)