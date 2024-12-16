import pymysql
import pytest

class TestProductFilter:

    @pytest.fixture(scope="function", autouse=True)
    def setup_and_teardown(self):
        """
        Thiết lập cơ sở dữ liệu và chuẩn bị dữ liệu kiểm thử.
        """
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="laptrinhweb2"
        )
        self.cursor = self.conn.cursor()

        self.cursor.execute("DELETE FROM sanpham")
        self.cursor.execute("DELETE FROM category")
        self.conn.commit()

        self.cursor.execute("INSERT INTO category (id, category_name) VALUES (1, 'Laptop')")
        self.cursor.execute("INSERT INTO category (id, category_name) VALUES (2, 'Phụ Kiện')")
        self.conn.commit()
        self.cursor.execute("INSERT INTO sanpham (id, TenSP, GiaSP, category_id) VALUES (1, 'Laptop A', 10000000, 1)")
        self.cursor.execute("INSERT INTO sanpham (id, TenSP, GiaSP, category_id) VALUES (2, 'Laptop B', 18000000, 1)")
        self.cursor.execute("INSERT INTO sanpham (id, TenSP, GiaSP, category_id) VALUES (3, 'Laptop C', 25000000, 1)")
        self.cursor.execute("INSERT INTO sanpham (id, TenSP, GiaSP, category_id) VALUES (4, 'Phụ Kiện A', 8000000, 2)")
        self.conn.commit()

        yield

        self.cursor.execute("DELETE FROM sanpham")
        self.cursor.execute("DELETE FROM category")
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def test_filter_price_only(self):
        """
        Kiểm tra lọc sản phẩm chỉ theo giá.
        """
        self.cursor.execute("SELECT * FROM sanpham WHERE GiaSP >= 5000000 AND GiaSP <= 15000000")
        result = self.cursor.fetchall()
        assert len(result) == 2  

        self.cursor.execute("SELECT * FROM sanpham WHERE GiaSP >= 15000000 AND GiaSP <= 20000000")
        result = self.cursor.fetchall()
        assert len(result) == 1  

        self.cursor.execute("SELECT * FROM sanpham WHERE GiaSP >= 20000000")
        result = self.cursor.fetchall()
        assert len(result) == 1  

    def test_filter_category_and_price(self):
        """
        Kiểm tra lọc sản phẩm theo danh mục và giá.
        """
        self.cursor.execute("""
            SELECT * FROM sanpham WHERE category_id = 1 AND GiaSP >= 5000000 AND GiaSP <= 15000000
        """)
        result = self.cursor.fetchall()
        assert len(result) == 1  

        self.cursor.execute("""
            SELECT * FROM sanpham WHERE category_id = 2 AND GiaSP >= 5000000 AND GiaSP <= 15000000
        """)
        result = self.cursor.fetchall()
        assert len(result) == 1  

    def test_no_matching_products(self):
        """
        Kiểm tra khi không có sản phẩm khớp.
        """
        self.cursor.execute("SELECT * FROM sanpham WHERE category_id = 2 AND GiaSP >= 20000000")
        result = self.cursor.fetchall()
        assert len(result) == 0  
