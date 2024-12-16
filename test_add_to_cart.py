import pymysql
import pytest

class TestAddToCart:

    @pytest.fixture(scope="function", autouse=True)
    def setup_and_teardown(self):
        """
        Thiết lập kết nối cơ sở dữ liệu và dọn dẹp trước/sau mỗi bài kiểm thử.
        """
      
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="laptrinhweb2"
        )
        self.cursor = self.conn.cursor()

        self.cursor.execute("DELETE FROM cart")
        self.conn.commit()


        self.cursor.execute("INSERT INTO sanpham (id, MaSP, TenSP) VALUES (1, 'SP001', 'Laptop Test')")
        self.conn.commit()

        yield

        
        self.cursor.execute("DELETE FROM sanpham")
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def add_to_cart(self, product_id, username):
        """
        Logic thêm sản phẩm vào giỏ hàng.
        """

        if not username:
            return False  

        
        self.cursor.execute("SELECT * FROM sanpham WHERE id = %s", (product_id,))
        product = self.cursor.fetchone()
        if not product:
            return False  

        masp = product[1] 
        soluongSP = 1


        self.cursor.execute("SELECT * FROM cart WHERE masp = %s AND taikhoan = %s", (masp, username))
        cart_item = self.cursor.fetchone()

        if cart_item:
         
            self.cursor.execute(
                "UPDATE cart SET soluong = soluong + 1 WHERE masp = %s AND taikhoan = %s", (masp, username)
            )
        else:
         
            self.cursor.execute(
                "INSERT INTO cart (taikhoan, masp, soluong) VALUES (%s, %s, %s)", (username, masp, soluongSP)
            )

        self.conn.commit()
        return True

    def test_user_not_logged_in(self):
        """
        Kiểm tra trường hợp người dùng chưa đăng nhập.
        """
        username = ""  
        product_id = 1 

     
        assert self.add_to_cart(product_id, username) == False

    def test_product_not_exist(self):
        """
        Kiểm tra trường hợp sản phẩm không tồn tại.
        """
        username = "test_user"
        product_id = 999  

        assert self.add_to_cart(product_id, username) == False

    def test_add_new_product_to_cart(self):
        """
        Kiểm tra thêm sản phẩm mới vào giỏ hàng.
        """
        username = "test_user"
        product_id = 1 

        assert self.add_to_cart(product_id, username) == True

      
        self.cursor.execute("SELECT * FROM cart WHERE masp = 'SP001' AND taikhoan = %s", (username,))
        cart_item = self.cursor.fetchone()
        assert cart_item is not None
        assert cart_item[2] == "SP001"
        assert cart_item[3] == 1 

    def test_add_existing_product_to_cart(self):
        """
        Kiểm tra tăng số lượng khi sản phẩm đã tồn tại trong giỏ hàng.
        """
        username = "test_user"
        product_id = 1  


        self.add_to_cart(product_id, username)


        self.add_to_cart(product_id, username)

    
        self.cursor.execute("SELECT soluong FROM cart WHERE masp = 'SP001' AND taikhoan = %s", (username,))
        result = self.cursor.fetchone()
        assert result[0] == 2  
