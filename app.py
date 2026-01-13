from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import re
import os # Import os for environment variables

app = Flask(__name__)
CORS(app)

# MongoDB Connection - Railway par host karte waqt environment variables use karna best hai
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://hospitalemergancy:hospitalemergancy@cluster0.wqgziaf.mongodb.net/?appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client['hospital_db']
hospitals_col = db['hospitals']

@app.route('/api/search', methods=['GET'])
def search_hospitals():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])

    search_pattern = re.compile(query, re.IGNORECASE)

    search_filter = {
        "$or": [
            {"fullName": search_pattern},
            {"name": search_pattern},
            {"address": search_pattern},
            {"Facility Name": search_pattern}
        ]
    }

    results = hospitals_col.find(search_filter).limit(50)

    output = []
    for h in results:
        name = h.get("fullName") or h.get("name") or h.get("Facility Name") or "Unknown Hospital"
        address = h.get("address") or h.get("Facility Address") or h.get("State") or "India"
        
        output.append({
            "fullName": name,
            "phone": h.get("phone", "011-2345678"),
            "address": address,
            "availableBeds": str(h.get("availableBeds", "10+")),
            "profilePhoto": h.get("profilePhoto", ""),
            "type": "India" 
        })
    
    return jsonify(output)

@app.route('/api/register_hospital', methods=['POST'])
def register_hospital():
    data = request.json
    if not data or 'email' not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    if hospitals_col.find_one({"email": data['email']}):
        return jsonify({"message": "Hospital already registered"}), 200

    hospitals_col.insert_one(data)
    return jsonify({"message": "Successfully Registered"}), 201

if __name__ == '__main__':
    # Railway ke liye PORT variable check karna zaroori hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
