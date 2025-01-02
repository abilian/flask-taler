import pytest
from flask import Flask
from flask_taler import Taler

TALER_MERCHANT_BACKEND_URL = "https://merchant.taler.example.com"
TALER_EXCHANGE_URL = "https://taler.example.com"
TALER_MERCHANT_API_KEY = "test_api"


# Mock Taler backend responses for testing
@pytest.fixture
def mock_taler_backend(requests_mock):
    requests_mock.post(
        'https://merchant.taler.example.com/private/orders',
        json={'order_id': 'test-order-123', 'payment_redirect_url': 'https://pay.taler.example.com/pay/123'},
        status_code=200
    )
    requests_mock.get(
        'https://merchant.taler.example.com/private/orders/test-order-123',
        json={'payment_redirect_url': 'https://pay.taler.example.com/pay/123'},
        status_code=200
    )
    requests_mock.post(
        'https://merchant.taler.example.com/private/orders/test-order-123/refund',
        json={'refund_id': 'refund-456'},
        status_code=200
    )
    return requests_mock


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['TALER_EXCHANGE_URL'] = 'https://taler.example.com'
    app.config['TALER_MERCHANT_BACKEND_URL'] = 'https://merchant.taler.example.com'
    app.config['TALER_MERCHANT_API_KEY'] = 'test_api_key'
    return app


@pytest.fixture
def taler(app):
    return Taler(app)


def test_create_order(taler, mock_taler_backend):
    order = taler.create_order(amount=10.0, product_description="Test Product")
    assert order['order_id'] == 'test-order-123'
    assert order['payment_redirect_url'] == 'https://pay.taler.example.com/pay/123'


def test_get_payment_url(taler, mock_taler_backend):
    payment_url = taler.get_payment_url('test-order-123')
    assert payment_url == 'https://pay.taler.example.com/pay/123'


def test_process_refund(taler, mock_taler_backend):
    refund = taler.process_refund('test-order-123')
    assert refund['refund_id'] == 'refund-456'
