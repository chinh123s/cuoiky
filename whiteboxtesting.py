import requests
import mysql.connector 
import pytest

# URL của ứng dụng
BASE_URL = "http://localhost/ProjectWeb/"

# Kết nối tới database để kiểm tra trực tiếp
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "LaptrinhWeb2"
}

def db_execute_query(query, fetch_one=False):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchone() if fetch_one else cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result

@pytest.fixture
def setup_test_data():
    """Thêm dữ liệu kiểm thử."""
    query = """
    INSERT INTO sanpham (id, TenSP, MoTaSP, GiaSP, HinhSP, category_id)
    VALUES (9999, 'Sản phẩm test', 'Mô tả test', 100000, 'test.jpg', 1);
    """
    db_execute_query(query)
    yield
    # Dọn dẹp dữ liệu sau kiểm thử
    db_execute_query("DELETE FROM sanpham WHERE id = 9999;")

def test_delete_product_as_admin(setup_test_data):
    """Kiểm thử xóa sản phẩm với quyền admin."""
    params = {
        "del": 1,
        "id": 9999
    }
    cookies = {"user_role": "admin"}  # Mô phỏng người dùng admin

    # Gửi yêu cầu HTTP GET
    response = requests.get(BASE_URL, params=params, cookies=cookies)
    assert response.status_code == 200
    assert "Sản phẩm đã xóa thành công" in response.text

    # Kiểm tra xem sản phẩm đã bị xóa khỏi DB
    result = db_execute_query("SELECT * FROM sanpham WHERE id = 9999", fetch_one=True)
    assert result is None

def test_delete_product_without_permission():
    """Kiểm thử xóa sản phẩm khi không có quyền admin."""
    params = {
        "del": 1,
        "id": 9999
    }
    cookies = {"user_role": "user"}  # Mô phỏng người dùng không phải admin

    response = requests.get(BASE_URL, params=params, cookies=cookies)
    assert response.status_code == 403  # HTTP 403 Forbidden
    assert "Bạn không có quyền xóa sản phẩm" in response.text
