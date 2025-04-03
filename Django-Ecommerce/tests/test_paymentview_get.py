import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.shortcuts import reverse
from core.models import Order
from core.views import PaymentView

@pytest.mark.django_db
def test_payment_view_get_with_billing_address():
    factory = RequestFactory()
    user = User.objects.create_user(username="testuser", password="password")

    # Fake order with billing address
    order = Order.objects.create(user=user, ordered=False, billing_address="123 Street")

    # Tạo request GET
    request = factory.get(reverse("payment"))
    request.user = user

    # Xử lý messages trong request
    setattr(request, "_messages", FallbackStorage(request))

    # Gọi method get() trực tiếp
    response = PaymentView.as_view()(request)

    # Kiểm tra template được render đúng
    assert response.status_code == 200
    assert "payment.html" in [t.name for t in response.template_name]

@pytest.mark.django_db
def test_payment_view_get_without_billing_address():
    factory = RequestFactory()
    user = User.objects.create_user(username="testuser", password="password")

    # Fake order nhưng KHÔNG có billing address
    order = Order.objects.create(user=user, ordered=False, billing_address="")

    # Tạo request GET
    request = factory.get(reverse("payment"))
    request.user = user

    # Xử lý messages trong request
    setattr(request, "_messages", FallbackStorage(request))

    # Gọi method get() trực tiếp
    response = PaymentView.as_view()(request)

    # Kiểm tra redirect về checkout
    assert response.status_code == 302
    assert response.url == reverse("core:checkout")
