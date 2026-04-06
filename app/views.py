from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
import json , stripe 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Product
from django.conf import settings
def detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0
        user_not_login = "show"
        user_login = "hidden"

    id = request.GET.get('id', '')
    product = Product.objects.get(id=id)  # ✅ Lấy sản phẩm chính

    # ✅ Lấy các sản phẩm tương tự (cùng danh mục, trừ chính nó)
    related_products = Product.objects.filter(
        category__in=product.category.all()
    ).exclude(id=product.id)[:4]

    categories = Category.objects.filter(is_sub=False)

    context = {
        'products': [product],          # dùng list để tương thích template cũ
        'related_products': related_products,  # ✅ thêm vào
        'categories': categories,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login
    }
    return render(request, 'app/detail.html', context)


# Tìm kiếm sản phẩm
def category(request):
    categories = Category.objects.filter(is_sub=False)
    active_category = request.GET.get('category', '')  # Lấy slug danh mục từ URL

    # Kiểm tra nếu active_category có giá trị
    if active_category:
        # Lọc sản phẩm dựa vào slug của Category
        categories_with_slug = Category.objects.filter(slug=active_category)
        products = Product.objects.filter(category__in=categories_with_slug)  # Lọc sản phẩm thuộc về những Category có slug này
    else:
        products = Product.objects.all()  # Nếu không có slug thì hiển thị tất cả sản phẩm

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0
        user_not_login = "show"
        user_login = "hidden"
        customer = None  # Ensure 'customer' is defined when the user is not logged in
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
        'categories': categories,
        'products': products,
        'active_category': active_category
    }
    return render(request, 'app/category.html', context)
def search(request):
    searched = ''  # Đảm bảo rằng searched luôn được định nghĩa
    keys = []  # Danh sách sản phẩm mặc định là rỗng

    if request.method == "POST":
        searched = request.POST["searched"]  # Lấy từ form tìm kiếm
        keys = Product.objects.filter(name__icontains=searched)  # Lọc sản phẩm theo tên, không phân biệt chữ hoa chữ thường

    # Kiểm tra xem người dùng đã đăng nhập chưa
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items  # Lấy tổng số lượng sản phẩm trong giỏ hàng
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}  # Giả lập dữ liệu nếu người dùng không đăng nhập
        cartItems = 0  # Tổng số sản phẩm mặc định là 0
        user_not_login = "show"
        user_login = "hidden"
        # Không cần tạo 'order' nếu người dùng chưa đăng nhập
    categories = Category.objects.filter(is_sub=False)
    products = Product.objects.all()  # Lấy danh sách sản phẩm để hiển thị
    return render(request, 'app/search.html', {
        "searched": searched,
        "keys": keys,
        'categories': categories,
        'products': products,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login
    })

# Hàm đăng ký người dùng mới
def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        user_not_login = "hidden"
        user_login = "show"
        if form.is_valid():
            form.save()
            return redirect('login')
    user_not_login = "show"
    user_login = "hidden"
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0
    context = {'form': form,
               'user_not_login': user_not_login,

        'user_login': user_login,
        'items': items,
        'order': order,
        'cartItems': cartItems,
               }
    return render(request, 'app/register.html', context)


# Hàm đăng nhập
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        user_not_login = "hidden"
        user_login = "show"
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'user or password not correct!')
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0
    user_not_login = "show"
    user_login = "hidden"
    context = { 'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,

        'user_login': user_login
        }
    return render(request, 'app/login.html', context)


# Hàm đăng xuất
def logoutPage(request):
    logout(request)
    return redirect('login')


# Trang chủ
def home(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items  # Lấy tổng số lượng sản phẩm trong giỏ hàng
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}  # Giả lập dữ liệu nếu người dùng không đăng nhập
        cartItems = 0  # Tổng số sản phẩm mặc định là 0
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub =False)
    active_category = request.GET.get('category','')

    products = Product.objects.all()  # Lấy danh sách sản phẩm để hiển thị
    context = {
        'categories': categories,
        'active_category': active_category,
        'products': products,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login
    }
    return render(request, 'app/home.html', context)


# Giỏ hàng
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        user_not_login = "hidden"
        user_login = "show"
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = 0
        user_not_login = "show"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub =False)
    context = {
        'categories': categories,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login
    }
    return render(request, 'app/cart.html', context)

from django.http import JsonResponse
import json
from .models import Product, Order, OrderItem

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    # Lấy user (đăng nhập)
    customer = request.user

    # Lấy sản phẩm
    product = Product.objects.get(id=productId)

    # Lấy hoặc tạo Order (giỏ hàng hiện tại)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    # Tìm item trong giỏ
    orderItem = OrderItem.objects.filter(order=order, product=product).first()

    # Nếu chưa có mà không phải hành động delete thì tạo
    if not orderItem and action != 'delete':
        orderItem = OrderItem.objects.create(order=order, product=product, quantity=0)

    # Xử lý hành động
    if action == 'add':
        orderItem.quantity += 1
        orderItem.save()

    elif action == 'remove':
        orderItem.quantity -= 1
        if orderItem.quantity <= 0:
            orderItem.delete()
        else:
            orderItem.save()

    elif action == 'delete':
        if orderItem:
            orderItem.delete()
            print(f"🗑️ Deleted product {productId} from cart")
        else:
            print("⚠️ Tried to delete non-existent item")

    # Trả dữ liệu về
    cart_items = order.get_cart_items if hasattr(order, 'get_cart_items') else 0
    return JsonResponse({'message': 'Cart updated', 'cart_items': cart_items})



from django.shortcuts import render, redirect
from django.utils.timezone import now, localtime
from django.contrib import messages
from .models import Order, OrderItem, Category, Invoice  # Đảm bảo Invoice đã được thêm

def checkout(request):
    # Kiểm tra nếu người dùng đã đăng nhập
    user = request.user if request.user.is_authenticated else None
    user_not_login = "hidden" if user else "show"
    user_login = "show" if user else "hidden"

    # Kiểm tra giỏ hàng
    cartItems = 0
    order = None
    items = []

    if user:
        try:
            order = Order.objects.get(customer=user, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
        except Order.DoesNotExist:
            messages.error(request, "Giỏ hàng của bạn trống!")
            return redirect('cart')  # Nếu không có đơn hàng, chuyển về giỏ hàng

    # Xử lý POST request khi người dùng bấm "Đặt hàng"
    if request.method == 'POST':
        if order:
            current_time = localtime(now())
            order.date_order = current_time
            order.complete = True
            order.save()

            # Tạo hóa đơn cho đơn hàng
            invoice = Invoice.objects.create(
                order=order,
                invoice_date=current_time,
                customer=user,
                total_amount=order.get_cart_total
            )
            messages.success(
                request,
                f"Đặt hàng thành công! Hóa đơn #{invoice.id} đã được tạo lúc {current_time.strftime('%H:%M:%S, %d-%m-%Y')}"
            )
            return redirect('invoice_detail', id=invoice.id)  # Chuyển hướng đến trang hóa đơn chi tiết
        else:
            messages.error(request, "Không có giỏ hàng để đặt!")
            return redirect('cart')

    # Lấy danh mục sản phẩm để hiển thị
    categories = Category.objects.filter(is_sub=False)

    # Truyền thông tin vào context
    context = {
        'categories': categories,
        'items': items,
        'order': order,
        'cartItems': cartItems,
        'user_not_login': user_not_login,
        'user_login': user_login,
    }

    return render(request, 'app/checkout.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Invoice

def invoice_detail(request, id):
    # Sử dụng get_object_or_404 để đảm bảo nếu không tìm thấy hóa đơn sẽ trả về 404
    invoice = get_object_or_404(Invoice, id=id)
    
    # Truyền đối tượng invoice vào template
    return render(request, 'app/invoice_detail.html', {'invoice': invoice})




def order_history(request):
    if request.user.is_authenticated:
        user = request.user
        orders = Order.objects.filter(customer=user, complete=True).order_by('-date_order')
        categories = Category.objects.filter(is_sub=False)
        user_not_login = "hidden"
        user_login = "show"
    else:
        messages.warning(request, "Bạn cần đăng nhập để xem lịch sử đơn hàng!")
        return redirect('login')

    # Truyền hóa đơn tương ứng cho từng đơn hàng
    for order in orders:
        try:
            order.invoice = order.invoice  # Gắn invoice vào từng order
        except Invoice.DoesNotExist:
            order.invoice = None  # Nếu chưa có hóa đơn thì gán None

    context = {
        'orders': orders,
        'categories': categories,
        'user_not_login': user_not_login,
        'user_login': user_login,
    }
    return render(request, 'app/order_history.html', context)

def search_suggestions(request):
    query = request.GET.get('term', '').strip()
    suggestions = []

    if query:
        products = Product.objects.filter(name__icontains=query)[:5]  # Lấy 5 sản phẩm đầu
        suggestions = [{'id': p.id, 'name': p.name} for p in products]

    return JsonResponse(suggestions, safe=False)

import stripe
from django.conf import settings
from django.shortcuts import render, redirect

stripe.api_key = settings.STRIPE_SECRET_KEY


import stripe
from django.http import JsonResponse

def create_checkout_session(request):

    order = Order.objects.get(
        customer=request.user,
        complete=False
    )

    total_price = min(int(order.get_cart_total), 99999999)


    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'vnd',
                'product_data': {
                    'name': 'Thanh toán đơn hàng'
                },
                'unit_amount': total_price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/success/',
        cancel_url='http://127.0.0.1:8000/payment/',
    )

    return redirect(session.url)





def payment(request):

    if request.user.is_authenticated:

        order, created = Order.objects.get_or_create(
            customer=request.user,
            complete=False
        )

        context = {
            'order': order
        }

        return render(request, 'app/payment.html', context)

    else:
        return redirect('login')

def success(request):

    order = Order.objects.get(customer=request.user, complete=False)

    order.complete = True
    order.status = 'approved'
    order.transaction_id = "stripe_payment"

    order.save()

    return render(request, 'app/success.html')

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from django.shortcuts import get_object_or_404
##Endpoint Get - lay san pham
@api_view(['GET'])
def get_products(request):

    products = Product.objects.all()

    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)

##Endpoint Post - Tạo sản phẩm
@api_view(['POST'])
def create_product(request):

    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)

##Endpoint Delete - Xóa sản phẩm
@api_view(['DELETE'])
def delete_product(request, pk):

    product = get_object_or_404(Product, id=pk)

    product.delete()

    return Response({"message": "Product deleted successfully"})
