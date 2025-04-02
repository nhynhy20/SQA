
# @pytest.mark.django_db
# def test_login_success(client):
#     """Kiểm thử đăng nhập thành công"""
#     User.objects.create_user(username="testuser", password="passw")  # Tạo user

#     success = client.login(username="testuser", password="passw")
#     assert success is True  # Kiểm tra nếu đăng nhập thành công

#     # In danh sách user trong database test
#     print("Users in test DB:", list(User.objects.values("id", "username")))


# @pytest.mark.django_db
# def test_login_fail_wrong_password(client):
#     """Kiểm thử đăng nhập với mật khẩu sai"""
#     user = User.objects.create_user(username="testuser", password="password123")  # Tạo user
#     user.save()

#     success = client.login(username="testuser", password="wrongpassword")
#     assert success is False  # Đăng nhập phải thất bại

#     # In danh sách user trong database test
#     print("Users in test DB:", list(User.objects.values("id", "username")))


# @pytest.mark.django_db
# def test_login_fail_user_not_exist(client):
#     """Kiểm thử đăng nhập với tài khoản không tồn tại"""
#     success = client.login(username="nouser", password="password123")
#     assert success is False  # Đăng nhập phải thất bại

#     # In danh sách user trong database test
#     print("Users in test DB:", list(User.objects.values("id", "username")))
