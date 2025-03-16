from flask import Flask, request, jsonify, Response
import random
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature TEXT,
            format TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Insert some dummy data
def insert_dummy_data():
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM weather_data")  # Clear old data
    cities = ['delhi', 'Mumbai', 'hyderabad', 'Bengaluru', 'Chennai']
    for city in cities:
        temp = f"{random.randint(15, 40)}°C"
        format_choice = random.choice(['xml', 'json'])
        cursor.execute("INSERT INTO weather_data (city, temperature, format) VALUES (?, ?, ?)", (city, temp, format_choice))
    conn.commit()
    conn.close()

# Flask route
@app.route('/weather/<city>/', methods=['GET'])
def get_weather(city):
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute("SELECT temperature, format FROM weather_data WHERE city = ?", (city,))
    result = cursor.fetchone()
    conn.close()

    if result:
        temperature, response_format = result
        if response_format == "xml":
            xml_response = f"<weather><city>{city}</city><temperature>{temperature}</temperature></weather>"
            return Response(xml_response, mimetype='application/xml')
        else:  # Default to JSON
            return jsonify({'city': city, 'temperature': temperature})
    else:
        return jsonify({'error': 'City not found'})

if __name__ == "__main__":
    init_db()
    insert_dummy_data()
    app.run()
