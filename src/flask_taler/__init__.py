from flask import current_app, g, request, abort
import requests
from urllib.parse import urljoin
import hmac
import hashlib
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set the logging level to INFO

# Create a file handler
file_handler = logging.FileHandler('flask_taler.log')
file_handler.setLevel(logging.INFO)

# Create a console handler (optional, for console output)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class Taler(object):
    """
    Flask extension for integrating GNU Taler payments.
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

        # Configuration parameters (defaults can be set here)
        self.exchange_url = None
        self.merchant_backend_url = None
        self.merchant_api_key = None
        self.default_currency = "EUR"
        self.webhook_secret = None  # Add a secret for webhook verification

    def init_app(self, app):
        """Initialize the extension with the Flask app."""
        # Load configuration from Flask app's config
        self.exchange_url = app.config['TALER_EXCHANGE_URL']
        self.merchant_backend_url = app.config['TALER_MERCHANT_BACKEND_URL']
        self.merchant_api_key = app.config['TALER_MERCHANT_API_KEY']
        self.default_currency = app.config.get('TALER_DEFAULT_CURRENCY')
        self.webhook_secret = app.config.get('TALER_WEBHOOK_SECRET')  # Webhook secret

        # Register the extension with the app
        app.extensions['taler'] = self

        # Register a before_request handler to make 'taler' available in the request context
        app.before_request(self._set_taler_in_request_context)

    def _set_taler_in_request_context(self):
        """Makes the 'taler' instance available in the request context (g)."""
        if 'taler' not in g:
            g.taler = self

    def create_order(self, amount, currency=None, order_id=None, product_description=None, fulfillment_url=None,
                     metadata=None, auto_refund=None, pay_deadline=None, refund_deadline=None, public_reorder_url=None):
        """
        Create a new payment order with the Taler merchant backend.

        Args:
            amount (float): The amount to be paid.
            currency (str, optional): The currency code (e.g., "EUR"). Defaults to the configured default currency.
            order_id (str, optional): An optional custom order ID. If not provided, the backend will generate one.
            product_description (str, optional): A description of the product or service.
            fulfillment_url (str, optional): The URL to redirect to after successful payment.
            metadata (dict, optional): Additional metadata to store with the order.
            auto_refund (dict, optional): Auto refund time.
            pay_deadline (dict, optional): Pay deadline timestamp.
            refund_deadline (dict, optional): Refund deadline timestamp.
            public_reorder_url (str, optional): Public URL for reordering.

        Returns:
            dict: The order details returned by the Taler backend, including the order ID and payment URL.
        """
        currency = currency or self.default_currency

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {self.merchant_api_key}',
            'Content-Type': 'application/json',
        }

        order_data = {
            "order": {
                "summary": product_description,
                "order_id": order_id,
                "amount": f"{currency}:{amount}",
                "public_reorder_url": public_reorder_url,
                "fulfillment_url": fulfillment_url,
                "refund_deadline": refund_deadline,
                "pay_deadline": pay_deadline,
                "auto_refund": auto_refund,
            },
            "create_token": True,
        }

        if metadata is not None:
            order_data['order']['metadata'] = metadata

        url = urljoin(self.merchant_backend_url, '/private/orders')
        try:
            response = requests.post(url, headers=headers, json=order_data)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating order: {e}")
            raise

    def get_payment_url(self, order_id):
        """
        Retrieves the payment URL for a given order ID.

        Args:
            order_id (str): The ID of the order.

        Returns:
            str: The payment URL, or None if the order is not found or not payable.
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {self.merchant_api_key}',
        }

        url = urljoin(self.merchant_backend_url, f'/private/orders/{order_id}')

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            order_data = response.json()
            return order_data.get('taler_pay_uri')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving payment URL for order {order_id}: {e}")
            return None

    def get_order(self, order_id):
        """
        Retrieves the order details for a given order ID.

        Args:
            order_id (str): The ID of the order.

        Returns:
            dict: The order details, or None if the order is not found.
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {self.merchant_api_key}',
        }

        url = urljoin(self.merchant_backend_url, f'/private/orders/{order_id}')

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving order {order_id}: {e}")
            return None

    def process_refund(self, order_id, amount=None, reason=None):
        """
        Initiates a refund for a given order ID.

        Args:
            order_id (str): The ID of the order to refund.
            amount (float, optional): The amount to refund. If None, a full refund is issued.
            reason (str, optional): The reason for the refund.

        Returns:
            dict: The refund response from the Taler backend.
        """
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {self.merchant_api_key}',
            'Content-Type': 'application/json',
        }

        refund_data = {}
        if amount is not None:
            refund_data['refund'] = str(amount)
        if reason is not None:
            refund_data['reason'] = reason

        url = urljoin(self.merchant_backend_url, f'/private/orders/{order_id}/refund')

        try:
            response = requests.post(url, headers=headers, json=refund_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error processing refund for order {order_id}: {e}")
            raise

    def verify_webhook_signature(self, payload, signature):
        """
        Verifies the HMAC signature of a Taler webhook payload.

        Args:
            payload (bytes): The raw payload data.
            signature (str): The signature from the 'X-Taler-Signature' header.

        Returns:
            bool: True if the signature is valid, False otherwise.
        """

        if not self.webhook_secret:
            logger.error("Webhook secret is not configured.")
            return False

        # Taler uses sha256
        calculated_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(calculated_signature, signature)

    def handle_webhook(self):
        """
        Handles incoming Taler webhooks.

        This method should be called from a Flask view that is registered as the webhook endpoint
        in the Taler merchant backend.

        Example usage in a Flask app:

            from flask import Blueprint

            taler_bp = Blueprint('taler', __name__, url_prefix='/taler')

            @taler_bp.route('/webhook', methods=['POST'])
            def taler_webhook():
                try:
                    result = current_app.extensions['taler'].handle_webhook()
                    if result:
                        return "OK", 200
                    else:
                        return "Signature Verification Failed", 400
                except Exception as e:
                    current_app.logger.error(f"Error processing Taler webhook: {e}")
                    return "Internal Server Error", 500

        Returns:
            bool: True if the webhook was processed successfully, False otherwise.
        """
        data = request.get_data()
        signature = request.headers.get('X-Taler-Signature')

        if not signature or not self.verify_webhook_signature(data, signature):
            logger.error("Invalid webhook signature.")
            abort(400, "Invalid signature")  # Signature verification failed

        try:
            event = json.loads(data.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON payload in webhook.")
            abort(400, "Invalid JSON payload")

        logger.info(f"Received Taler webhook: {event}")

        # Process the event
        if event.get("type") == "payment.succeeded":
            order_id = event["payload"]["order_id"]
            logger.info(f"Payment succeeded for order: {order_id}")
        elif event.get("type") == "payment.failed":
            order_id = event["payload"]["order_id"]
            logger.info(f"Payment failed for order: {order_id}")
        # handle other event types

        return True  # Webhook processed successfully

    # ... other methods for wallet operations, Dolibarr integration, etc. ...
