# updated app.py
import os
from flask import Flask, render_template,request
import pickle
import numpy as np
import re
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# load the port info from env vars
port = int(os.environ.get("PORT",5000))

# make the flask app
app = Flask(__name__)

# Load the model
model = pickle.load(open('models/model.pkl', 'rb'))
# Load the vectorizer
vectorizer = pickle.load(open('models/vectorizer.pkl','rb'))

    
@app.route('/')
def home():
    return render_template('index.html',result=None)


@app.route('/predict', methods=['POST'])
def predict():
    # Get user input
    input_text = request.form['text']

    # Preprocess the text
    text = input_text.lower()
    print("Cleaned text:", text)

    # Convert text into Bag of Words features
    features = vectorizer.transform([text])

    print("Non-zero features:", features.nnz)

    # Predict
    result = model.predict(features)[0]

    print("Prediction:", result)
    print("Probabilities:", model.predict_proba(features))

    # Convert model output to user-friendly label
    label_map = {
        "happiness": "Happy",
        "sadness": "Sad",
        "neutral": "Neutral"
    }

    final_result = label_map.get(result, result)

    # Create audit folder if it doesn't exist
    os.makedirs("audit", exist_ok=True)

    # Save prediction in text file
    with(open("audit/predictions.txt", "a")) as f:
        f.write(f"Input: {input_text} | Prediction: {final_result}\n")
        
    # Display result on webpage
    return render_template("index.html", result=final_result)    

if __name__ == "__main__":
    # Start the Flask app 
    # start the app on the specified port 
    app.run(host="0.0.0.0", port=port)