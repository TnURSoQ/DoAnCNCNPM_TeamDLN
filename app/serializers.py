from rest_framework import serializers
from .models import Product, Category, Order


# Product Serializer + Validation
class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Tên sản phẩm phải lớn hơn 3 ký tự")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Giá phải lớn hơn 0")
        return value


# Category Serializer + Validation
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'

    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Tên danh mục quá ngắn")
        return value


# Order Serializer + Validation
class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'

    def validate_status(self, value):
        valid_status = ['pending', 'shipping', 'completed']

        if value not in valid_status:
            raise serializers.ValidationError("Trạng thái không hợp lệ")

        return value
