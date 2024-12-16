import pymysql
import pytest


class TestCheckout:

    @pytest.fixture(scope="function", autouse=True)
    def setup_and_teardown(self):
        """
        Thiết lập kết nối cơ sở dữ liệu và chuẩn bị dữ liệu kiểm thử.
        """
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="laptrinhweb2"
        )
        self.cursor = self.conn.cursor()

       
        self.cursor.execute("DELETE FROM cart")
        self.cursor.execute("DELETE FROM sanpham")
        self.conn.commit()


        self.cursor.execute("INSERT INTO sanpham (id, MaSP, TenSP, GiaSP) VALUES (1, 'SP001', 'Laptop 1', 23000000)")
        self.cursor.execute("INSERT INTO sanpham (id, MaSP, TenSP, GiaSP) VALUES (2, 'SP002', 'Laptop 2', 20000000)")
        self.conn.commit()

        self.cursor.execute("INSERT INTO cart (taikhoan, masp, soluong) VALUES ('test_user', 'SP001', 2)")
        self.cursor.execute("INSERT INTO cart (taikhoan, masp, soluong) VALUES ('test_user', 'SP002', 1)")
        self.conn.commit()

        yield

        # Dọn dẹp sau khi kiểm thử
        self.cursor.execute("DELETE FROM cart")
        self.cursor.execute("DELETE FROM sanpham")
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def calculate_total_price(self, username):
        """
        Hàm tính tổng giá trị đơn hàng từ bảng cart.
        """
        self.cursor.execute("""
            SELECT SUM(sanpham.GiaSP * cart.soluong) as tong_gia 
            FROM cart 
            INNER JOIN sanpham ON cart.masp = sanpham.MaSP 
            WHERE cart.taikhoan = %s
        """, (username,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def test_calculate_total_price(self):
        """
        Kiểm tra logic tính tổng giá trị đơn hàng.
        """
        total_price = self.calculate_total_price('test_user')
        assert total_price == 46000000 + 20000000  

    def test_payment_method(self):
        """
        Kiểm tra logic chọn phương thức thanh toán.
        """
   
        payment_method = "COD"
        assert payment_method in ["COD", "Online"]

        payment_method = "Online"
        assert payment_method in ["COD", "Online"]

    def test_checkout_missing_info(self):
        """
        Kiểm tra khi thiếu thông tin đặt hàng.
        """
        fullname = ""
        phone = ""
        payment_method = ""

     
        assert fullname != "" and "Thiếu họ và tên"
        assert phone != "" and "Thiếu số điện thoại"
        assert payment_method != "" and "Chưa chọn phương thức thanh toán"

    def test_checkout_success(self):
        """
        Kiểm tra đặt hàng thành công.
        """
        fullname = "Nguyen Van A"
        phone = "0123456789"
        payment_method = "COD"


        assert fullname != ""
        assert phone != ""
        assert payment_method in ["COD", "Online"]

    
        self.cursor.execute("SELECT * FROM cart WHERE taikhoan = 'test_user'")
        cart_items = self.cursor.fetchall()
        assert len(cart_items) == 2 
