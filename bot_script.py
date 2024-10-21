import openai
import os
import json
import sqlite3
import spacy
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def fetch_data(query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message["content"].strip()

def verify_data(new_data, existing_data):
    return True  # or False

def create_table(db_path='data.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS info (id INTEGER PRIMARY KEY, data TEXT)''')
    conn.commit()
    conn.close()

def store_data(data, db_path='data.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO info (data) VALUES (?)''', (data,))
    conn.commit()
    conn.close()

def load_data(db_path='data.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT data FROM info''')
    rows = cursor.fetchall()
    conn.close()
    return rows

def analyze_query(query):
    doc = nlp(query)
    entities = [ent.text for ent in doc.ents]
    main_subjects = [chunk.text for chunk in doc.noun_chunks]
    return entities, main_subjects

def normalize(text):
    return ' '.join(text.lower().split())

def main():
    create_table()
    while True:
        query = input("Enter your query: ")
        if query.lower() == 'exit':
            break
        
        existing_data = load_data()
        normalized_query = normalize(query)
        
        # Check existing data for a normalized match
        found = False
        for row in existing_data:
            if normalized_query in normalize(row[0]):
                print("Data found in database: ", row[0])
                found = True
                break
        
        if not found:
            fetched_data = fetch_data(query)
            print("Output data from OpenAI: ", fetched_data)
            
            # Analyze and summarize the query
            entities, main_subjects = analyze_query(query)
            print(f"Entities: {entities}")
            print(f"Main Subjects: {main_subjects}")
            
            # Ask user to verify and save data
            user_input = input("Do you want to save this data to the database? (yes/no): ")
            if user_input.lower() == 'yes':
                store_data(fetched_data)
                print("Data stored successfully.")
            else:
                print("Data not stored.")

if __name__ == '__main__':
    main()


