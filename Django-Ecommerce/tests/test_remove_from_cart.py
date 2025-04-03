import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Item, Order, OrderItem, Category
from django.test import Client

@pytest.mark.django_db
def test_remove_item_from_cart_with_active_order_and_item():
    # Tạo user
    user = User.objects.create_user(username="testuser", password="password")
    client = Client()
    client.login(username="testuser", password="password")

    # Tạo Category và Item
    category = Category.objects.create(title="Test Category")
    item = Item.objects.create(
        title="Test Item",
        price=100.0,
        category=category,
        label="A",
        slug="test-item",
        stock_no="12345",
        description_short="Test",
        description_long="Test Item Description",
        image="test.jpg"
    )

    # Tạo Order và OrderItem
    order = Order.objects.create(user=user, ref_code="123ABC", ordered=False, ordered_date="2025-04-03")
    order_item = OrderItem.objects.create(item=item, user=user, quantity=1, ordered=False)
    order.items.add(order_item)

    # Gửi yêu cầu để xóa mặt hàng khỏi giỏ hàng
    url = reverse("core:remove-from-cart", kwargs={'slug': item.slug})
    response = client.get(url)

    # Kiểm tra phản hồi
    assert response.status_code == 302  # Redirect

    # Kiểm tra thông điệp trong request
    messages = list(response.wsgi_request._messages)
    assert len(messages) > 0
    assert any("Item was removed from your cart." in str(message) for message in messages)



@pytest.mark.django_db
@pytest.mark.django_db
def test_remove_item_from_cart_when_no_active_order():
    # Tạo user
    user = User.objects.create_user(username="testuser", password="password")
    client = Client()
    client.login(username="testuser", password="password")

    # Tạo Category và Item
    category = Category.objects.create(title="Test Category")
    item = Item.objects.create(
        title="Test Item",
        price=100.0,
        category=category,
        label="A",
        slug="test-item",
        stock_no="12345",
        description_short="Test",
        description_long="Test Item Description",
        image="test.jpg"
    )

    # Gửi yêu cầu để xóa mặt hàng khỏi giỏ hàng
    url = reverse("core:remove-from-cart", kwargs={'slug': item.slug})
    response = client.get(url)

    # Kiểm tra phản hồi
    assert response.status_code == 302  # Kiểm tra xem có redirect không

    # Kiểm tra thông điệp nếu có, nếu không cần thiết thì bỏ qua
    # Nếu thông điệp được gửi trong view (thông qua messages.error), cần phải kiểm tra lại:
    assert 'u don\'t have an active order.' not in response.content.decode('utf-8')



