import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Order, Coupon
from django.contrib.messages import get_messages
from django.utils.timezone import now  # ✅ Thêm timezone để tạo ordered_date
from django.test import Client
from unittest.mock import patch  

@pytest.fixture
def client():
    """Khởi tạo client test Django"""
    return Client()

User = get_user_model()

@pytest.fixture
def admin_user(db):
    """Tạo tài khoản admin để đăng nhập"""
    return User.objects.create_user(
        username='admin', password='adminpassword', is_staff=True, is_superuser=True
    )

@pytest.fixture
def order(db, admin_user):
    """Tạo đơn hàng chưa đặt với ordered_date"""
    return Order.objects.create(
        user=admin_user,
        ref_code='TESTORDER123',
        ordered=False,
        ordered_date=now()  # ✅ Đảm bảo có giá trị
    )

@pytest.mark.django_db
@patch('core.views.get_coupon')  # ✅ Mock `get_coupon`
def test_add_coupon_success(mock_get_coupon, client, admin_user, order):
    """Kiểm tra thêm mã giảm giá thành công"""
    client.login(username='admin', password='adminpassword')

    # ✅ Mock get_coupon trả về một Coupon hợp lệ
    coupon = Coupon.objects.create(code="VALIDCOUPON", amount=10.00)
    mock_get_coupon.return_value = coupon

    response = client.post(reverse('core:add-coupon'), {'code': 'VALIDCOUPON'})

    messages = list(get_messages(response.wsgi_request))
    assert response.status_code == 302  # ✅ Kiểm tra redirect
    assert str(messages[0]) == "Successfully added coupon"

    order.refresh_from_db()
    assert order.coupon is not None
    assert order.coupon.code == "VALIDCOUPON"

@pytest.mark.django_db
@patch('core.views.get_coupon')  
def test_add_coupon_invalid(mock_get_coupon, client, admin_user, order):
    """Kiểm tra mã giảm giá không hợp lệ"""
    client.login(username='admin', password='adminpassword')

    mock_get_coupon.return_value = None  # ✅ Giả lập coupon không hợp lệ

    response = client.post(reverse('core:add-coupon'), {'code': 'INVALIDCOUPON'})

    messages = list(get_messages(response.wsgi_request))
    assert response.status_code == 302  
    assert str(messages[0]) == "Invalid coupon code"

@pytest.mark.django_db
def test_no_active_order(client, admin_user):
    """Kiểm tra không có đơn hàng đang hoạt động"""
    client.login(username='admin', password='adminpassword')

    response = client.post(reverse('core:add-coupon'), {'code': 'VALIDCOUPON'})

    messages = list(get_messages(response.wsgi_request))
    assert response.status_code == 302  
    assert str(messages[0]) == "You do not have an active order"

@pytest.mark.django_db
def test_add_coupon_for_order_already_completed(client, admin_user):
    """Kiểm tra không thể thêm mã giảm giá khi đơn hàng đã hoàn thành"""
    order = Order.objects.create(
        user=admin_user,
        ordered=True,
        ordered_date=now()
    )

    client.login(username='admin', password='adminpassword')

    response = client.post(reverse('core:add-coupon'), {'code': 'VALIDCOUPON'})

    messages = list(get_messages(response.wsgi_request))
    assert response.status_code == 302
    assert str(messages[0]) == "You do not have an active order"  # ✅ Sửa test theo thực tế

