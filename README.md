# Flask-Taler: GNU Taler Integration for Flask

[![PyPI version](https://badge.fury.io/py/flask-taler.svg)](https://badge.fury.io/py/flask-taler)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


`Flask-Taler` is a Flask extension that simplifies the integration of [GNU Taler](https://taler.net/), a privacy-preserving electronic payment system, into your Flask web applications. This extension provides a convenient way to create payment orders, handle payment redirects, process refunds, and manage callbacks from the Taler system.


> NOT READY FOR RELEASE


## Features

*   **Easy Order Creation:**  Create Taler payment orders with just a few lines of code.
*   **Payment URL Retrieval:** Obtain payment URLs to redirect users to the Taler wallet for payment.
*   **Refund Handling:** Process full or partial refunds for completed transactions.
*   **Callback Handling:**  Implement routes to handle payment success and failure callbacks.
*   **Webhook Support (Recommended):** Integrate with Taler's webhook functionality for real-time payment status updates.
*   **Error Handling:** Robust error handling and logging for debugging.
*   **Secure Configuration:** Store API keys and other sensitive information securely.

## Installation

```bash
pip install flask-taler
```

## Configuration

Configure the `Flask-Taler` extension using the following parameters in your Flask app's configuration (`app.config`):

*   `TALER_EXCHANGE_URL`: The URL of the Taler exchange.
*   `TALER_MERCHANT_BACKEND_URL`: The URL of your Taler merchant backend.
*   `TALER_MERCHANT_API_KEY`: Your Taler merchant API key.
*   `TALER_DEFAULT_CURRENCY`: The default currency for orders (e.g., "EUR").

**Example:**

```python
app = Flask(__name__)
app.config['TALER_EXCHANGE_URL'] = 'https://exchange.taler.example.com'
app.config['TALER_MERCHANT_BACKEND_URL'] = 'https://merchant.taler.example.com'
app.config['TALER_MERCHANT_API_KEY'] = 'your_api_key_here'
app.config['TALER_DEFAULT_CURRENCY'] = 'USD'
```

It's highly recommended to store sensitive information like API keys in environment variables rather than directly in your code. You can use libraries like `python-dotenv` to manage environment variables.

## Usage

Here's a basic example of how to use `Flask-Taler` to create an order and handle payment:

```python
from flask import Flask, render_template, request, redirect, url_for
from flask_taler import Taler

app = Flask(__name__)
# ... (Configuration as described above) ...

taler = Taler(app)

@app.route('/buy/<int:product_id>')
def buy_product(product_id):
    # 1. Retrieve product information from your database
    product = get_product_from_db(product_id)

    # 2. Create a Taler payment order
    order = taler.create_order(
        amount=product.price,
        currency=product.currency,
        order_id=f"product-{product_id}", # Optional custom order ID
        product_description=product.name,
        fulfillment_url=url_for('payment_success', product_id=product_id, _external=True) # URL to redirect to after successful payment.
    )

    # 3. Get the payment URL and redirect the user
    payment_url = taler.get_payment_url(order['order_id'])
    if payment_url:
        return redirect(payment_url)
    else:
        return "Error creating order or getting payment URL."

@app.route('/payment/success/<int:product_id>')
def payment_success(product_id):
    # 4. (Recommended) Verify the payment status using Taler's webhooks.
    # For this demo, we'll assume the payment was successful.

    product = get_product_from_db(product_id)
    return f"Thank you for purchasing {product.name}!"

@app.route('/refund/<order_id>')
def refund_order(order_id):
    # 5. Initiate a refund for a given order
    refund_result = taler.process_refund(order_id)
    if refund_result:
        return f"Refund for order {order_id} processed successfully."
    else:
        return f"Error processing refund for order {order_id}."

# ... (Helper function to get product details from the database) ...
def get_product_from_db(product_id):
    # Replace with your actual database query logic
    # This is just a placeholder example
    products = {
        1: {'name': 'Awesome T-Shirt', 'price': 25.0, 'currency': 'EUR'},
        2: {'name': 'Cool Mug', 'price': 10.0, 'currency': 'USD'},
    }
    return products.get(product_id)

if __name__ == '__main__':
    app.run(debug=True)
```

**Explanation:**

1. **Retrieve Product:** The `buy_product` route first fetches product details (replace `get_product_from_db` with your actual database logic).
2. **Create Order:** It then uses `taler.create_order()` to create a new payment order with the Taler backend. You need to provide the amount, currency, an optional order ID, product description, and a fulfillment URL (where the user will be redirected after successful payment).
3. **Redirect to Payment:** `taler.get_payment_url()` retrieves the URL for the Taler payment page. The user is redirected to this URL to complete the payment.
4. **Handle Success (Webhook Recommended):** The `payment_success` route is a placeholder for handling successful payments. Ideally, you should use Taler's webhook functionality to receive real-time notifications about payment status changes. In a real application, you would verify the payment status with the Taler backend before fulfilling the order.
5. **Refund:** The `refund_order` route demonstrates how to initiate a refund using `taler.process_refund()`.

**Important Notes:**

*   **Webhooks:** For production environments, it's crucial to implement webhooks to receive asynchronous notifications from Taler about payment status changes. This ensures that you don't rely solely on user redirects for order fulfillment.
*   **Error Handling:** The example code includes basic error handling. You should expand this to handle various error scenarios and provide appropriate feedback to the user.
*   **Security:** Always store your Taler API key securely, preferably as an environment variable.


## Conceptual Overview

The `flask-taler` extension provides a simple and intuitive API for Flask developers to:

1. **Initialize Taler:** Configure the extension with necessary parameters like the Taler exchange URL, merchant backend URL, API keys, etc.
2. **Create Orders:** Easily create payment orders with details like amount, currency, product description, and fulfillment URL.
3. **Get Payment URL:** Obtain a payment URL that redirects the user to the Taler wallet for payment.
4. **Handle Payment Callbacks:**  Define routes to handle payment success/failure callbacks from the Taler system.
5. **Process Refunds:** Issue full or partial refunds for completed transactions.
6. **Manage Wallet Operations:** Handle wallet operations.


## API Reference

### `Taler` Class

**`__init__(self, app=None)`:** Initializes the extension. If `app` is provided, it calls `init_app(app)`.

**`init_app(self, app)`:** Initializes the extension with the Flask app. Loads configuration from `app.config`.

**`create_order(self, amount, currency=None, order_id=None, product_description=None, fulfillment_url=None, metadata=None)`:** Creates a payment order.
    *   `amount` (float): The amount to be paid.
    *   `currency` (str, optional): The currency code. Defaults to `TALER_DEFAULT_CURRENCY`.
    *   `order_id` (str, optional): A custom order ID.
    *   `product_description` (str, optional): A description of the product or service.
    *   `fulfillment_url` (str, optional): The URL to redirect to after successful payment.
    *   `metadata` (dict, optional): Additional metadata to store with the order.
    *   **Returns:** A dictionary containing the order details from the Taler backend.

**`get_payment_url(self, order_id)`:** Retrieves the payment URL for an order.
    *   `order_id` (str): The ID of the order.
    *   **Returns:** The payment URL (str) or `None` if the order is not found or not payable.

**`process_refund(self, order_id, amount=None)`:** Initiates a refund.
    *   `order_id` (str): The ID of the order to refund.
    *   `amount` (float, optional): The amount to refund. If `None`, a full refund is issued.
    *   **Returns:** The refund response from the Taler backend.


## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues on the project's [GitHub repository](your-repo-url).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Further Development / Roadmap

*   **Wallet Operations:** Add methods to the extension to interact with Corporate and Collaborator wallets for managing funds, transfers, etc.
*   **Dolibarr Integration:** Create helper functions or classes to map Taler orders and payments to Dolibarr invoices and transactions.
*   **Advanced Features:** Implement support for features like session-bound payments, repurchase detection, and more complex order customization options offered by the Taler API.
*   **Testing:** Write comprehensive unit and integration tests to ensure the extension works correctly and handles various scenarios.
*   **Documentation:** Provide clear and detailed documentation for the extension, including usage examples, API reference, and troubleshooting tips.
