import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse
from core.models import Category


@pytest.mark.django_db
def test_category_creation_valid_data():
    """Test tạo category thành công với dữ liệu hợp lệ"""
    category = Category.objects.create(
        title="Valid Category Title",
        slug="valid-category-slug",
        description="Valid category description",
        image="test_image.jpg",
    )
    assert category.pk is not None
    assert category.title == "Valid Category Title"
    assert category.slug == "valid-category-slug"
    print("✅ SUCCESS: Tạo category thành công với dữ liệu hợp lệ")


@pytest.mark.django_db
def test_category_title_max_length():
    """Kiểm tra title category không vượt quá 100 ký tự"""
    long_title = "a" * 101
    with pytest.raises(ValidationError) as excinfo:
        category = Category(
            title=long_title,
            slug="test-slug",
            description="Test desc",
            image="test.jpg",
        )
        category.full_clean()
    assert "Ensure this value has at most 100 characters" in excinfo.value.messages[0]
    print("✅ SUCCESS: Không cho phép title category dài quá 100 ký tự")


@pytest.mark.django_db
def test_category_slug_unique():
    """Kiểm tra slug category phải là unique"""
    Category.objects.create(
        title="Category 1",
        slug="test-slug",
        description="Test desc 1",
        image="test1.jpg",
    )
    with pytest.raises(IntegrityError):
        Category.objects.create(
            title="Category 2",
            slug="test-slug",
            description="Test desc 2",
            image="test2.jpg",
        )
    print("✅ SUCCESS: Slug category là unique")


@pytest.mark.django_db
def test_category_title_required():
    """Kiểm tra title category là trường bắt buộc"""
    with pytest.raises(ValidationError) as excinfo:
        category = Category(slug="test-slug", description="Test desc", image="test.jpg")
        category.full_clean()
    assert "This field cannot be blank." in excinfo.value.messages[0]
    print("✅ SUCCESS: Title category là trường bắt buộc")


@pytest.mark.django_db
def test_category_slug_required():
    """Kiểm tra slug category là trường bắt buộc"""
    with pytest.raises(ValidationError) as excinfo:
        category = Category(
            title="Test Title", description="Test desc", image="test.jpg"
        )
        category.full_clean()
    assert "This field cannot be blank." in excinfo.value.messages[0]
    print("✅ SUCCESS: Slug category là trường bắt buộc")


@pytest.mark.django_db
def test_category_slug_valid_format():
    """Kiểm tra slug category có định dạng hợp lệ (ví dụ: chỉ chữ cái, số, gạch ngang)"""
    invalid_slugs = ["invalid slug", "slug!", "slug#@", "slug*name", "with_uppercase"]
    for slug in invalid_slugs:
        with pytest.raises(ValidationError) as excinfo:
            category = Category(
                title="Test Title", slug=slug, description="Test desc", image="test.jpg"
            )
            category.full_clean()
        assert (
            "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens."
            in excinfo.value.messages[0]
        )
        print(f"✅ SUCCESS: Không cho phép slug '{slug}' không hợp lệ")


@pytest.mark.django_db
def test_category_is_active_default_value():
    """Kiểm tra giá trị mặc định của is_active là True"""
    category = Category.objects.create(
        title="Test Category",
        slug="test-category",
        description="Test desc",
        image="test.jpg",
    )
    assert category.is_active is True
    print("✅ SUCCESS: Giá trị mặc định của is_active là True")


@pytest.mark.django_db
def test_category_str_method():
    """Kiểm tra method __str__ trả về title của category"""
    category = Category.objects.create(
        title="Test Category Title",
        slug="test-category",
        description="Test desc",
        image="test.jpg",
    )
    assert str(category) == "Test Category Title"
    print("✅ SUCCESS: Method __str__ trả về title")


@pytest.mark.django_db
def test_category_get_absolute_url_method():
    """Kiểm tra method get_absolute_url trả về URL đúng"""
    category = Category.objects.create(
        title="Test Category Title",
        slug="test-category",
        description="Test desc",
        image="test.jpg",
    )
    expected_url = reverse(
        "core:category", kwargs={"slug": "test-category"}
    )  # Đảm bảo namespace 'core' khớp với urls.py
    assert category.get_absolute_url() == expected_url
    print("✅ SUCCESS: Method get_absolute_url trả về URL đúng")


@pytest.mark.django_db
def test_category_view_get_request_success(client, valid_category, valid_item):
    """Test GET request đến CategoryView thành công (status 200, template, context)"""
    url = reverse("category", kwargs={"slug": valid_category.slug})
    response = client.get(url)

    assert response.status_code == 200
    assert "category.html" in [t.name for t in response.templates]
    assert response.context["category_title"] == valid_category
    assert valid_item in response.context["object_list"]
    print("✅ SUCCESS: GET request thành công đến CategoryView")


@pytest.mark.django_db
def test_category_view_get_request_category_not_found(client):
    """Test GET request đến CategoryView trả về 404 khi category không tồn tại"""
    url = reverse("category", kwargs={"slug": "non-existent-category"})
    response = client.get(url)
    assert response.status_code == 404
    print("✅ SUCCESS: GET request trả về 404 khi category không tồn tại")
