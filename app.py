from flask import Flask, render_template, request, jsonify
from datetime import datetime
import uuid
import math

app = Flask(__name__)

gate_status = "Closed"
parking_records = {}
slot_status = {
    "G1": "empty",
    "G2": "occupied",
    "G3": "empty",
    "G4": "occupied",
    "G5": "empty",
    "G6": "empty",
    "G7": "empty",
    "G8": "empty",
}

@app.route('/update-slot', methods=['POST'])
def update_slot():
    global slot_status
    data = request.get_json()
    slot_id = data.get("slot")
    status = data.get("status")
    if slot_id in slot_status and status in ["occupied", "empty"]:
        slot_status[slot_id] = status
        print(f"Slot {slot_id} updated to {status}")
        return jsonify({"message": "Slot updated", "status": slot_status[slot_id]})
    return jsonify({"error": "Invalid slot or status"}), 400

@app.route('/get-slot-status')
def get_slot_status():
    return jsonify(slot_status)

@app.route('/')
def home():
    return render_template('index.html', gate_status=gate_status)

@app.route('/gate', methods=['POST'])
def control_gate():
    global gate_status
    action = request.json.get('action')
    if action == "open":
        gate_status = "Opened"
    elif action == "close":
        gate_status = "Closed"
    return jsonify({"status": gate_status})

@app.route('/enter', methods=['POST'])
def enter_parking():
    empty_slot = next((slot for slot, status in slot_status.items() if status == "empty"), None)
    if empty_slot is None:
        return jsonify({"error": "Semua slot penuh"}), 403

    code = f"{empty_slot}-{str(uuid.uuid4())[:8]}"
    parking_records[code] = datetime.now()
    return jsonify({"code": code})

@app.route('/get-servo-status')
def get_servo_status():
    print("ESP32 requested status")
    return jsonify({"angle": 70 if gate_status == "Opened" else 0})

@app.route('/calculate', methods=['POST'])
def calculate_parking():
    code = request.json.get('code')
    if code not in parking_records:
        return jsonify({"error": "Kode parkir tidak ditemukan"}), 404

    masuk = parking_records[code]
    sekarang = datetime.now()
    lama_jam = math.ceil((sekarang - masuk).total_seconds() / 60 )
    tarif = lama_jam * 3000

    return jsonify({
        "time": f"{lama_jam} menit",
        "tariff": f"Rp {tarif:,}"
    })

@app.route('/get-all-slots')
def get_all_slots():
    return jsonify(slot_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)