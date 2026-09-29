import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#
def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
    
    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}
    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    expected_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = expected_order

    result = order_tracker.get_order_by_id("ORD001")

    assert result == expected_order
    mock_storage.get_order.assert_called_once_with("ORD001")


def test_get_order_by_id_returns_none_when_order_does_not_exist(
    order_tracker, mock_storage
):
    # mock_storage.get_order already returns None by default.
    result = order_tracker.get_order_by_id("MISSING")

    assert result is None
    mock_storage.get_order.assert_called_once_with("MISSING")

def test_update_order_status_changes_status(order_tracker, mock_storage):
    order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = order

    result = order_tracker.update_order_status("ORD001", "shipped")

    assert result["status"] == "shipped"
    mock_storage.save_order.assert_called_once_with(
        "ORD001",
        {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "shipped",
        },
    )


def test_update_order_status_raises_error_if_order_does_not_exist(
    order_tracker, mock_storage
):
    # The fixture's mock get_order returns None by default.
    with pytest.raises(
        ValueError, match="Order with ID 'MISSING' not found."
    ):
        order_tracker.update_order_status("MISSING", "shipped")

    mock_storage.save_order.assert_not_called()

def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    expected_orders = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending",
        },
        "ORD002": {
            "order_id": "ORD002",
            "item_name": "Mouse",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": "shipped",
        },
    }
    mock_storage.get_all_orders.return_value = expected_orders

    result = order_tracker.list_all_orders()

    assert result == expected_orders
    mock_storage.get_all_orders.assert_called_once_with()


def test_list_orders_by_status_returns_only_matching_orders(
    order_tracker, mock_storage
):
    shipped_order = {
        "order_id": "ORD002",
        "item_name": "Mouse",
        "quantity": 2,
        "customer_id": "CUST002",
        "status": "shipped",
    }
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending",
        },
        "ORD002": shipped_order,
    }

    result = order_tracker.list_orders_by_status("shipped")

    assert result == [shipped_order]
    mock_storage.get_all_orders.assert_called_once_with()