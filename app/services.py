from .models import Product

def create_product(name, price):
    return Product.objects.create(name=name, price=price)

def get_product(product_id):
    return Product.objects.get(id=product_id)

def update_product(product_id, name, price):
    product = Product.objects.get(id=product_id)
    product.name = name
    product.price = price
    product.save()
    return product

def delete_product(product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return True
