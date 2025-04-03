import pytest
from django.urls import reverse
from django.test import Client
from core.models import Category, Item

@pytest.mark.django_db
def test_shop_view_shows_all_items():
    # Tạo Category
    category = Category.objects.create(title="Test Category")

    # Tạo một số Item
    Item.objects.create(
        title="Test Item 1",
        price=100.0,
        category=category,
        label="A",
        slug="test-item-1",
        stock_no="12345",
        description_short="Test 1",
        description_long="Test Item Description 1",
        image="test1.jpg"
    )
    Item.objects.create(
        title="Test Item 2",
        price=150.0,
        category=category,
        label="B",
        slug="test-item-2",
        stock_no="12346",
        description_short="Test 2",
        description_long="Test Item Description 2",
        image="test2.jpg"
    )

    # Gửi yêu cầu đến view Shop
    url = reverse("core:shop")
    client = Client()
    response = client.get(url)

    # Kiểm tra phản hồi
    assert response.status_code == 200  # Kiểm tra mã trạng thái là 200
    assert len(response.context['object_list']) == 2  # Kiểm tra số sản phẩm
    assert 'Test Item 1' in response.content.decode()  # Kiểm tra rằng sản phẩm xuất hiện trong response
    assert 'Test Item 2' in response.content.decode()

@pytest.mark.django_db
def test_shop_view_pagination():
    # Tạo Category
    category = Category.objects.create(title="Test Category")

    # Tạo hơn 6 Item để kiểm tra phân trang
    for i in range(10):
        Item.objects.create(
            title=f"Test Item {i+1}",
            price=100.0,
            category=category,
            label="A",
            slug=f"test-item-{i+1}",
            stock_no=f"12345{i+1}",
            description_short=f"Test {i+1}",
            description_long=f"Test Item Description {i+1}",
            image=f"test{i+1}.jpg"
        )

    # Gửi yêu cầu đến view Shop
    url = reverse("core:shop")
    client = Client()
    response = client.get(url)

    # Kiểm tra phản hồi
    assert response.status_code == 200  # Kiểm tra mã trạng thái là 200
    assert len(response.context['object_list']) == 6  # Kiểm tra rằng chỉ có 6 sản phẩm được hiển thị
    assert 'Test Item 1' in response.content.decode()  # Kiểm tra sản phẩm đầu tiên xuất hiện
    assert 'Test Item 6' in response.content.decode()  # Kiểm tra sản phẩm thứ 6 xuất hiện

@pytest.mark.django_db
def test_shop_view_uses_correct_template():
    # Tạo Category
    category = Category.objects.create(title="Test Category")

    # Tạo một số Item
    Item.objects.create(
        title="Test Item 1",
        price=100.0,
        category=category,
        label="A",
        slug="test-item-1",
        stock_no="12345",
        description_short="Test 1",
        description_long="Test Item Description 1",
        image="test1.jpg"
    )

    # Gửi yêu cầu đến view Shop
    url = reverse("core:shop")
    client = Client()
    response = client.get(url)

    # Kiểm tra phản hồi
    assert response.status_code == 200  # Kiểm tra mã trạng thái là 200
    assert "shop.html" in [t.name for t in response.templates]  # Kiểm tra tên template


@pytest.mark.django_db
def test_shop_view_no_items():
    # Gửi yêu cầu đến ShopView khi không có sản phẩm nào
    url = reverse("core:shop")
    client = Client()
    response = client.get(url)

    # Kiểm tra phản hồi
    assert response.status_code == 200  # Kiểm tra mã trạng thái HTTP 200
    assert len(response.context['object_list']) == 0  # Đảm bảo không có sản phẩm nào trong danh sách

    # Kiểm tra không có thẻ <div class="block2"> nào xuất hiện trong HTML
    assert '<div class="block2">' not in response.content.decode()
