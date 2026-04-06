from django.test import TestCase
from .models import Product
from .services import create_product, get_product, update_product, delete_product


class ProductServiceTest(TestCase):

    # Test 1: Tạo sản phẩm
    def test_create_product(self):
        product = create_product("Nike Air", 200)
        self.assertEqual(product.name, "Nike Air")
        self.assertEqual(product.price, 200)

    # Test 2: Lấy sản phẩm
    def test_get_product(self):
        product = Product.objects.create(name="Adidas", price=300)
        found = get_product(product.id)
        self.assertEqual(found.name, "Adidas")

    # Test 3: Cập nhật sản phẩm
    def test_update_product(self):
        product = Product.objects.create(name="Puma", price=150)
        updated = update_product(product.id, "Puma New", 180)
        self.assertEqual(updated.name, "Puma New")
        self.assertEqual(updated.price, 180)

    # Test 4: Xóa sản phẩm
    def test_delete_product(self):
        product = Product.objects.create(name="Vans", price=120)
        result = delete_product(product.id)
        self.assertTrue(result)

    # Test 5: Kiểm tra sản phẩm đã bị xóa
    def test_product_deleted(self):
        product = Product.objects.create(name="Converse", price=250)
        delete_product(product.id)
        self.assertEqual(Product.objects.count(), 0)
