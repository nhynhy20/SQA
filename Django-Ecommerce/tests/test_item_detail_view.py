import pytest
from django.urls import reverse
from core.models import Item, Category
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
def test_item_get_absolute_url():
    # Tạo một category mẫu với các trường bắt buộc
    category = Category.objects.create(
        title="Test Category",  # Tạo title cho category
        slug="test-category",   # Tạo slug cho category
        description="This is a test category",  # Tạo description cho category
        image="path/to/image.jpg"  # Giả lập image (hoặc bạn có thể sử dụng hình ảnh giả lập)
    )
    
    # Giả lập hình ảnh cho sản phẩm (Item)
    image = SimpleUploadedFile(name="test_image.jpg", content=b"file_content", content_type="image/jpeg")
    
    # Tạo sản phẩm mẫu (Item)
    item = Item.objects.create(
        title="Test Item",
        price=100.0,
        category=category,
        label="A",
        slug="test-item",
        stock_no="123456",
        description_short="Short description",
        description_long="Long description",
        image=image,  # Sử dụng hình ảnh giả lập
    )

    # Kiểm tra URL trả về từ phương thức get_absolute_url của Item
    expected_url = reverse("core:product", kwargs={"slug": item.slug})
    assert item.get_absolute_url() == expected_url


@pytest.mark.django_db
def test_item_get_add_to_cart_url():
    # Tạo danh mục mẫu với các trường đúng
    category = Category.objects.create(
        title="Test Category",  # Sử dụng title thay vì name
        slug="test-category",   # Tạo slug cho category
        description="This is a test category",  # Tạo description cho category
        image="path/to/image.jpg"  # Giả lập image (hoặc bạn có thể sử dụng hình ảnh giả lập)
    )

    # Giả lập hình ảnh cho sản phẩm (Item)
    image = SimpleUploadedFile(name="test_image.jpg", content=b"file_content", content_type="image/jpeg")

    # Tạo sản phẩm mẫu (Item)
    item = Item.objects.create(
        title="Test Item",
        price=100.0,
        category=category,
        label="A",
        slug="test-item",
        stock_no="123456",
        description_short="Short description",
        description_long="Long description",
        image=image,  # Sử dụng hình ảnh giả lập
    )

    # Kiểm tra URL trả về từ phương thức get_add_to_cart_url của Item
    expected_url = reverse("core:add-to-cart", kwargs={"slug": item.slug})
    assert item.get_add_to_cart_url() == expected_url


@pytest.mark.django_db
def test_item_get_remove_from_cart_url():
    # Tạo danh mục mẫu với trường đúng
    category = Category.objects.create(
        title="Test Category",  # Sử dụng title thay vì name
        slug="test-category",   # Tạo slug cho category
        description="This is a test category",  # Tạo description cho category
        image="path/to/image.jpg"  # Giả lập image (hoặc bạn có thể sử dụng hình ảnh giả lập)
    )

    # Giả lập hình ảnh cho sản phẩm (Item)
    image = SimpleUploadedFile(name="test_image.jpg", content=b"file_content", content_type="image/jpeg")

    # Tạo sản phẩm mẫu (Item)
    item = Item.objects.create(
        title="Test Item",
        price=100.0,
        category=category,
        label="A",
        slug="test-item",
        stock_no="123456",
        description_short="Short description",
        description_long="Long description",
        image=image,  # Sử dụng hình ảnh giả lập
    )

    # Kiểm tra URL trả về từ phương thức get_remove_from_cart_url của Item
    expected_url = reverse("core:remove-from-cart", kwargs={"slug": item.slug})
    assert item.get_remove_from_cart_url() == expected_url


@pytest.mark.django_db
def test_item_category():
    # Tạo danh mục mẫu
    category = Category.objects.create(title="Test Category")
    
    # Tạo sản phẩm mẫu
    item = Item.objects.create(
        title="Test Item",
        price=100.0,
        category=category,
        label="A",
        slug="test-item",
        stock_no="123456",
        description_short="Short description",
        description_long="Long description",
        image="path/to/image.jpg",
    )

    # Kiểm tra nếu danh mục của sản phẩm đúng
    assert item.category == category


@pytest.mark.django_db
def test_item_is_active():
    # Tạo danh mục mẫu
    category = Category.objects.create(title="Test Category")
    
    # Tạo sản phẩm mẫu với is_active=False
    item = Item.objects.create(
        title="Test Item",
        price=100.0,
        category=category,
        label="A",
        slug="test-item",
        stock_no="123456",
        description_short="Short description",
        description_long="Long description",
        image="path/to/image.jpg",
        is_active=False
    )

    # Kiểm tra xem sản phẩm có được kích hoạt hay không
    assert item.is_active is False
