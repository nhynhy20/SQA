import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from core.views import CheckoutView
from core.models import Order, OrderItem, BillingAddress
from core.forms import CheckoutForm, CouponForm
from django.contrib.auth.models import User
from django.test import RequestFactory


@pytest.mark.django_db
class TestCheckoutView:
    """
    Class này chứa các test cho CheckoutView.
    Sử dụng pytest.mark.django_db để đảm bảo các test có thể truy cập database Django.
    """

    def setup_method(self):
        """
        Phương thức này được gọi trước mỗi test method trong class này.
        Nó thiết lập các đối tượng và dữ liệu cần thiết cho các test.
        """
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )  # Tạo một user test
        self.order = Order.objects.create(
            user=self.user, ordered_date=pytest.lazy_fixture("now")
        )  # Tạo một order test (chưa ordered), sử dụng lazy_fixture cho 'now'
        self.order_item = OrderItem.objects.create(
            item=pytest.lazy_fixture("item"), quantity=1, user=self.user, ordered=False
        )  # Tạo một order item, sử dụng lazy_fixture cho 'item'
        self.order.items.add(self.order_item)  # Thêm order item vào order

    @pytest.fixture(
        autouse=True
    )  # autouse=True để fixture này được áp dụng cho tất cả test methods trong class
    def set_up_fixtures(self, item, now):  # Inject các fixtures 'item' và 'now' vào đây
        """
        Fixture này được tự động áp dụng cho tất cả các test methods trong class này.
        Mục đích chính là để inject các fixtures 'item' và 'now' (nếu cần) vào class.
        Trong ví dụ này, fixtures đã được định nghĩa ở conftest.py hoặc file test, chỉ cần inject.
        """
        pass  # Fixtures đã được định nghĩa ở conftest.py hoặc file test, chỉ cần inject chúng

    def test_get_checkout_view_with_active_order(self, client):
        """
        Test GET request đến CheckoutView khi user có một order active (chưa thanh toán).
        Kiểm tra xem view trả về status code 200, template đúng, context đúng.
        """
        client.force_login(self.user)  # Đăng nhập user test
        url = reverse("checkout")  # Tạo URL cho view checkout
        response = client.get(url)  # Gửi GET request đến URL checkout

        assert response.status_code == 200  # Assert status code phải là 200 (OK)
        assert "checkout.html" in [
            t.name for t in response.templates
        ]  # Assert template 'checkout.html' được sử dụng
        assert isinstance(
            response.context["form"], CheckoutForm
        )  # Assert 'form' trong context là instance của CheckoutForm
        assert isinstance(
            response.context["couponform"], CouponForm
        )  # Assert 'couponform' trong context là instance của CouponForm
        assert (
            response.context["order"] == self.order
        )  # Assert 'order' trong context là order đã tạo trong setup
        assert (
            response.context["DISPLAY_COUPON_FORM"] is True
        )  # Assert biến DISPLAY_COUPON_FORM trong context là True

    def test_get_checkout_view_no_active_order(self, client):
        """
        Test GET request đến CheckoutView khi user không có order active.
        Kiểm tra xem view redirect về trang checkout và hiển thị message thông báo.
        """
        client.force_login(self.user)  # Đăng nhập user test
        Order.objects.filter(
            user=self.user, ordered=False
        ).delete()  # Xóa order active để user không có order nào
        url = reverse("checkout")  # Tạo URL cho view checkout
        response = client.get(url)  # Gửi GET request

        assert response.status_code == 302  # Assert status code phải là 302 (Redirect)
        assert response.url == reverse(
            "checkout"
        )  # Assert URL redirect là về trang checkout
        messages = list(
            get_messages(response.wsgi_request)
        )  # Lấy danh sách messages từ response
        assert len(messages) == 1  # Assert có đúng 1 message được gửi
        assert (
            str(messages[0]) == "You do not have an active order"
        )  # Assert message là "You do not have an active order"
        assert messages[0].level_tag == "info"  # Assert level của message là 'info'

    def test_post_checkout_view_valid_form_stripe_payment(self, client):
        """
        Test POST request đến CheckoutView với form hợp lệ và chọn phương thức thanh toán Stripe.
        Kiểm tra xem view redirect đến trang thanh toán Stripe, tạo BillingAddress, liên kết BillingAddress với Order.
        """
        client.force_login(self.user)  # Đăng nhập user test
        url = reverse("checkout")  # Tạo URL cho view checkout
        post_data = {  # Dữ liệu form hợp lệ
            "street_address": "Test Address",
            "apartment_address": "Apt 4B",
            "country": "US",
            "zip": "12345",
            "payment_option": "S",  # Stripe - Chọn phương thức thanh toán Stripe
        }
        response = client.post(url, post_data)  # Gửi POST request với dữ liệu form

        assert response.status_code == 302  # Assert status code phải là 302 (Redirect)
        assert response.url == reverse(
            "core:payment", kwargs={"payment_option": "stripe"}
        )  # Assert URL redirect là đến trang thanh toán Stripe
        billing_address = BillingAddress.objects.filter(
            user=self.user
        ).first()  # Lấy BillingAddress vừa được tạo cho user
        assert billing_address is not None  # Assert BillingAddress đã được tạo
        assert (
            billing_address.street_address == "Test Address"
        )  # Assert street_address của BillingAddress đúng
        assert (
            billing_address.address_type == "B"
        )  # Assert address_type của BillingAddress là 'B' (Billing)
        order = Order.objects.get(
            user=self.user, ordered=False
        )  # Lấy order active của user
        assert (
            order.billing_address == billing_address
        )  # Assert billing_address của order được cập nhật đúng

    def test_post_checkout_view_valid_form_paypal_payment(self, client):
        """
        Test POST request đến CheckoutView với form hợp lệ và chọn phương thức thanh toán PayPal.
        Tương tự như test trên, nhưng kiểm tra cho phương thức thanh toán PayPal.
        """
        client.force_login(self.user)  # Đăng nhập user test
        url = reverse("checkout")  # Tạo URL cho view checkout
        post_data = {  # Dữ liệu form hợp lệ
            "street_address": "Test Address",
            "apartment_address": "Apt 4B",
            "country": "US",
            "zip": "12345",
            "payment_option": "P",  # PayPal - Chọn phương thức thanh toán PayPal
        }
        response = client.post(url, post_data)  # Gửi POST request

        assert response.status_code == 302  # Assert status code là 302 (Redirect)
        assert response.url == reverse(
            "core:payment", kwargs={"payment_option": "paypal"}
        )  # Assert URL redirect đến trang thanh toán PayPal
        billing_address = BillingAddress.objects.filter(
            user=self.user
        ).first()  # Lấy BillingAddress vừa tạo
        assert billing_address is not None  # Assert BillingAddress đã được tạo
        assert (
            billing_address.street_address == "Test Address"
        )  # Assert street_address đúng
        assert billing_address.address_type == "B"  # Assert address_type là 'B'
        order = Order.objects.get(user=self.user, ordered=False)  # Lấy order active
        assert (
            order.billing_address == billing_address
        )  # Assert billing_address của order được cập nhật

    def test_post_checkout_view_invalid_form(self, client):
        """
        Test POST request đến CheckoutView với form không hợp lệ (thiếu street_address).
        Kiểm tra xem view vẫn ở trang checkout, form có lỗi, BillingAddress không được tạo.
        """
        client.force_login(self.user)  # Đăng nhập user test
        url = reverse("checkout")  # Tạo URL checkout
        post_data = {  # Dữ liệu form không hợp lệ (thiếu street_address)
            "street_address": "",  # Invalid - Trường bắt buộc bị bỏ trống
            "apartment_address": "Apt 4B",
            "country": "US",
            "zip": "12345",
            "payment_option": "S",
        }
        response = client.post(url, post_data)  # Gửi POST request

        assert (
            response.status_code == 200
        )  # Assert status code là 200 (vẫn ở trang checkout)
        assert "checkout.html" in [
            t.name for t in response.templates
        ]  # Assert template 'checkout.html' vẫn được render
        assert isinstance(
            response.context["form"], CheckoutForm
        )  # Assert 'form' trong context là CheckoutForm
        assert response.context["form"].errors  # Assert form có lỗi
        assert not BillingAddress.objects.filter(
            user=self.user
        ).exists()  # Assert không có BillingAddress nào được tạo

    def test_post_checkout_view_no_active_order(self, client):
        """
        Test POST request đến CheckoutView khi user không có order active.
        Kiểm tra xem view redirect đến trang order summary và hiển thị message lỗi.
        """
        client.force_login(self.user)  # Đăng nhập user test
        Order.objects.filter(user=self.user, ordered=False).delete()  # Xóa order active
        url = reverse("checkout")  # Tạo URL checkout
        post_data = {  # Dữ liệu form (không quan trọng vì không có order)
            "street_address": "Test Address",
            "apartment_address": "Apt 4B",
            "country": "US",
            "zip": "12345",
            "payment_option": "S",
        }
        response = client.post(url, post_data)  # Gửi POST request

        assert response.status_code == 302  # Assert status code là 302 (Redirect)
        assert response.url == reverse(
            "core:order-summary"
        )  # Assert URL redirect đến trang order summary
        messages = list(get_messages(response.wsgi_request))  # Lấy messages
        assert len(messages) == 1  # Assert có 1 message
        assert (
            str(messages[0]) == "You do not have an active order"
        )  # Assert message là "You do not have an active order"
        assert messages[0].level_tag == "error"  # Assert level của message là 'error'
        assert not BillingAddress.objects.filter(
            user=self.user
        ).exists()  # Assert không có BillingAddress nào được tạo
