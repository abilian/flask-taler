import requests
from urllib.parse import urljoin


class Taler(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

        # Configuration parameters (defaults can be set here)
        self.exchange_url = None
        self.merchant_backend_url = None
        self.merchant_api_key = None
        self.default_currency = "EUR"  # Or other suitable default

    def init_app(self, app):
        """Initialize the extension with the Flask app."""
        # Load configuration from Flask app's config
        self.exchange_url = app.config['TALER_EXCHANGE_URL']
        self.merchant_backend_url = app.config['TALER_MERCHANT_BACKEND_URL']
        self.merchant_api_key = app.config['TALER_MERCHANT_API_KEY']
        self.default_currency = app.config.get('TALER_DEFAULT_CURRENCY', self.default_currency)
        # ... other configuration parameters

        # Register the extension with the app
        app.extensions['taler'] = self

    def create_order(self, amount, currency=None, order_id=None, product_description=None, fulfillment_url=None,
                     metadata=None):
        """Create a new payment order with the Taler merchant backend.

        Args:
            amount (float): The amount to be paid.
            currency (str, optional): The currency code (e.g., "EUR"). Defaults to the configured default currency.
            order_id (str, optional): An optional custom order ID. If not provided, the backend will generate one.
            product_description (str, optional): A description of the product or service.
            fulfillment_url (str, optional): The URL to redirect to after successful payment.
            metadata (dict, optional): Additional metadata to store with the order.

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
            'price': {
                'amount': str(amount),  # Convert to string for JSON serialization
                'currency': currency,
            },
            'order_id': order_id,
            'summary': product_description,
            'fulfillment_url': fulfillment_url,
            'metadata': metadata,
        }

        url = urljoin(self.merchant_backend_url, '/private/orders')
        response = requests.post(url, headers=headers, json=order_data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        return response.json()

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
        response = requests.get(url, headers=headers)

        match response.status_code:
            case 200:
                return response.json()
            case 404:
                print(f"Order {order_id} not found.")
                return None
            case _:
                print(f"Error processing refund for order {order_id}: {response.status_code}")
                response.raise_for_status()


def process_refund(self, order_id, amount=None):
    """
    Initiates a refund for a given order ID.

    Args:
        order_id (str): The ID of the order to refund.
        amount (float, optional): The amount to refund. If None, a full refund is issued.

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
        refund_data['amount'] = str(amount)  # Convert to string

    url = urljoin(self.merchant_backend_url, f'/private/orders/{order_id}/refund')
    response = requests.post(url, headers=headers, json=refund_data)

    match response.status_code:
        case 200:
            return response.json()
        case 404:
            print(f"Order {order_id} not found.")
            return None
        case _:
            print(f"Error processing refund for order {order_id}: {response.status_code}")
            response.raise_for_status()

# ... other methods for handling callbacks, webhooks, wallet operations, etc.
