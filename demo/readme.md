# Flask-Taler Demo Application

This repository contains a simple demo application showcasing how to use the `flask-taler` extension to integrate GNU Taler payments into a Flask web application.

**Note:** This is a simplified example for demonstration purposes. It does not include production-ready features like webhook implementation, thorough error handling, or database integration.

## Overview

The demo application simulates a basic e-commerce scenario where users can purchase products. It demonstrates the following core functionalities of the `flask-taler` extension:

1. **Creating Payment Orders:** Initiating a Taler payment order when a user clicks the "Buy" button.
2. **Redirecting to Taler Wallet:** Redirecting the user to the Taler wallet to complete the payment.
3. **Handling Successful Payment (Simplified):** Displaying a "Thank You" message upon successful payment. (In a real application, you would use webhooks to verify payment status).
4. **Processing Refunds:** Demonstrating how to initiate a refund for a specific order.

## Prerequisites

*   Python 3.10 or higher
*   Flask
*   `flask-taler` (the extension itself)
*   `requests`
*   A running instance of a GNU Taler exchange and merchant backend. You can set these up locally for testing using the Taler source code and documentation.


## Configuration

To configure the demo application, either:

1. **Create a `config.py` file:** You need to configure the Taler connection parameters. Create a `config.py` file in the root directory of the demo app with the following content:

    ```python
    # config.py
    TALER_EXCHANGE_URL = 'https://your-taler-exchange-url'  # Replace with your Taler exchange URL
    TALER_MERCHANT_BACKEND_URL = 'https://your-taler-merchant-backend-url' # Replace with your Taler merchant backend URL
    TALER_MERCHANT_API_KEY = 'your_merchant_api_key' # Replace with your merchant API key
    TALER_DEFAULT_CURRENCY = 'EUR'  # Or your preferred default currency
    ```

    **Important:** Replace the placeholder values with your actual Taler exchange URL, merchant backend URL, and API key.

2. Or set **Environment Variables (Recommended):**
    For security, it is strongly recommended to store your `TALER_MERCHANT_API_KEY` as an environment variable instead of directly in the `config.py` file. You can set the environment variable in your shell before running the app:

     ```bash
     export TALER_MERCHANT_API_KEY="your_actual_api_key"
     ```

    Then, modify your `config.py` to read from the environment variable:

    ```python
    # config.py
    import os

    TALER_EXCHANGE_URL = 'https://your-taler-exchange-url'
    TALER_MERCHANT_BACKEND_URL = 'https://your-taler-merchant-backend-url'
    TALER_MERCHANT_API_KEY = os.environ.get('TALER_MERCHANT_API_KEY')
    TALER_DEFAULT_CURRENCY = 'EUR'
    ```

## Running the Demo

1. Make sure you have activated your virtual environment.
2. Run the Flask application:

    ```bash
    flask run
    ```

    This will start the development server.

3. Open your web browser and go to `http://127.0.0.1:5000/`. You should see the demo application.

## Using the Demo

The demo app presents a simple interface with a few products.

*   **Buy a Product:** Click the "Buy" button next to a product. This will:
    1. Create a Taler payment order using `taler.create_order()`.
    2. Retrieve the payment URL using `taler.get_payment_url()`.
    3. Redirect you to the Taler wallet for payment.

*   **Simulated Payment Success:** After completing the payment in the Taler wallet (you'll need a test wallet for this), you'll be redirected back to the `/payment/success/<product_id>` route. The demo app simply displays a "Thank You" message.

*   **Refund an Order:** The demo app also includes a `/refund/<order_id>` route that demonstrates how to initiate a refund using `taler.process_refund()`. You'll need to manually enter an order ID in the URL to test the refund functionality.

**Important:** This demo application uses a very basic product listing that is hardcoded in the `app.py` file. In a real application, you would fetch product data from a database.

## Code Structure

*   **`app.py`:** The main Flask application file. It contains:
    *   Flask app initialization and configuration.
    *   Initialization of the `Taler` extension.
    *   Routes for:
        *   `/` (displays the product list - very basic).
        *   `/buy/<int:product_id>` (creates an order and redirects to Taler).
        *   `/payment/success/<int:product_id>` (simulates successful payment handling).
        *   `/refund/<order_id>` (initiates a refund).
    *   A placeholder `get_product_from_db()` function (you would replace this with actual database interaction in a real app).
*   **`flask_taler.py`:**  The code for the `flask-taler` extension (you should have this file in your project).
*   **`requirements.txt`:** Lists the required Python packages.
*   **`config.py`:** Contains the Taler configuration parameters.
*   **`templates/`:**  A directory for Jinja2 templates, currently empty, as the demo does not use any.

## Limitations

*   **No Webhooks:** This demo does **not** implement webhooks for real-time payment verification. In a production application, you **must** use webhooks to ensure reliable order fulfillment.
*   **Simplified Product Handling:** The product list is hardcoded.
*   **Minimal Error Handling:** Error handling is very basic.
*   **No Database Integration:** There's no database interaction.
*   **No User Authentication:** The demo doesn't have user accounts or authentication.

## Further Development

To turn this demo into a more realistic application, you would need to:

1. **Implement Webhooks:** Add a route to handle Taler webhooks and verify payment status before fulfilling orders.
2. **Integrate a Database:** Store product information, user data, and order details in a database (e.g., PostgreSQL, MySQL, SQLite).
3. **Add User Authentication:** Implement user registration and login.
4. **Improve Error Handling:** Handle various error conditions gracefully and provide informative error messages to the user.
5. **Enhance the Frontend:** Create a more visually appealing and user-friendly frontend (potentially using templates and a JavaScript framework).
6. **(Optional) Implement Wallet Features:** If relevant to your application, add support for Corporate and Collaborator wallet operations using the `flask-taler` extension.
7. **(Optional) Integrate with Dolibarr ERP:** Add functionality to connect with Dolibarr for invoice and payment tracking.

This README provides a comprehensive guide to the `flask-taler` demo application. Remember to adapt and expand upon this example to create a secure and fully functional e-commerce application with GNU Taler integration.
