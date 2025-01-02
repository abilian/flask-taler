
from flask import Flask, render_template, request, redirect, url_for
from flask_taler import Taler

app = Flask(__name__)
app.config['TALER_EXCHANGE_URL'] = 'https://taler.example.com'  # Replace with actual URLs
app.config['TALER_MERCHANT_BACKEND_URL'] = 'https://merchant.taler.example.com'
app.config['TALER_MERCHANT_API_KEY'] = 'your_merchant_api_key'
app.config['TALER_DEFAULT_CURRENCY'] = 'EUR'

taler = Taler(app)


# Example route to create an order and redirect to payment
@app.route('/buy/<int:product_id>')
def buy_product(product_id):
    product = get_product_from_db(product_id)  # Replace with your product lookup logic

    order = taler.create_order(
        amount=product.price,
        order_id=f"prod-{product_id}",
        product_description=product.name,
        fulfillment_url=url_for('payment_success', product_id=product_id, _external=True)
    )

    payment_url = taler.get_payment_url(order['order_id'])
    if payment_url:
        return redirect(payment_url)
    else:
        return "Error creating order or getting payment URL."


# Example route to handle successful payment callback
@app.route('/payment/success/<int:product_id>')
def payment_success(product_id):
    # Verify the payment status with the Taler backend using webhooks (recommended) or polling
    # ... (Implementation for verification logic)
    # For demonstration, let's assume the payment was verified

    product = get_product_from_db(product_id)
    return f"Thank you for purchasing {product.name}!"


# Example route to issue a refund
@app.route('/refund/<order_id>')
def refund_order(order_id):
    refund_result = taler.process_refund(order_id)
    if refund_result:
        return f"Refund for order {order_id} processed successfully."
    else:
        return f"Error processing refund for order {order_id}."
