from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    order_data = request.get_json(silent=True)
    required_fields = ("order_id", "item_name", "quantity", "customer_id")

    if not isinstance(order_data, dict) or any(
        field not in order_data for field in required_fields
    ):
        return jsonify({"error": "Request must include order_id, item_name, quantity, and customer_id."}), 400

    try:
        order_tracker.add_order(
            order_data["order_id"],
            order_data["item_name"],
            order_data["quantity"],
            order_data["customer_id"],
            order_data.get("status", "pending"),
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 409

    return jsonify(order_tracker.get_order_by_id(order_data["order_id"])), 201

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        return jsonify({"error": f"Order with ID '{order_id}' not found."}), 404
    return jsonify(order), 200

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    update_data = request.get_json(silent=True)
    new_status = update_data.get("new_status") if isinstance(update_data, dict) else None
    if not isinstance(new_status, str) or not new_status.strip():
        return jsonify({"error": "Request must include a non-empty new_status."}), 400

    try:
        order = order_tracker.update_order_status(order_id, new_status)
    except ValueError as error:
        return jsonify({"error": str(error)}), 404
    return jsonify(order), 200

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    status = request.args.get("status")
    if status:
        orders = order_tracker.list_orders_by_status(status)
    else:
        orders = list(order_tracker.list_all_orders().values())
    return jsonify(orders), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
