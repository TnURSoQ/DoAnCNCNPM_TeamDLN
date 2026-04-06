from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.models import ChatHistory

import os
from dotenv import load_dotenv
import google.generativeai as genai


# Thay 'store.models' bằng tên app thực tế của bạn nếu khác
# Ví dụ: from products.models import Product
from app.models import Product 

# Tải biến môi trường từ file .env
load_dotenv()

# Lấy API key từ file .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Kiểm tra có key chưa
if not GEMINI_API_KEY:
    raise ValueError("❌ Thiếu GEMINI_API_KEY trong file .env")

# Cấu hình Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Khởi tạo model (nên dùng các model mới hơn như gemini-1.5-flash)
model = genai.GenerativeModel("gemini-3-flash-preview")

# =============================================================
# 🧠 HÀM TỰ ĐỘNG LẤY VÀ ĐỊNH DẠNG DỮ LIỆU SẢN PHẨM TỪ DATABASE
# =============================================================
def get_product_data_for_prompt():
    """
    Truy vấn tất cả sản phẩm từ database và định dạng chúng 
    thành một chuỗi markdown table cho AI.
    Hàm này đã được cập nhật để phù hợp với models.py của bạn.
    """
    # Lấy tất cả sản phẩm, và prefetch_related 'category' để tối ưu truy vấn
    products = Product.objects.prefetch_related('category').all()
    
    if not products:
        return "Hiện tại cửa hàng chưa có sản phẩm nào."

    # Bắt đầu bảng markdown
    product_list_str = "Dưới đây là danh sách các sản phẩm hiện có của cửa hàng:\n\n"
    product_list_str += "| Tên sản phẩm | Danh mục | Giá (VNĐ) | Mô tả chi tiết |\n"
    product_list_str += "|---|---|---|---|\n"

    # Thêm từng sản phẩm vào bảng
    for product in products:
        # Lấy danh sách các category và nối chúng lại thành một chuỗi
        categories = ', '.join([cat.name for cat in product.category.all()]) if product.category.exists() else "Chưa phân loại"
        
        # Định dạng giá tiền cho dễ đọc, chuyển từ Decimal về int
        price = f"{int(product.price):,}".replace(",", ".")
        
        # Thay đổi: sử dụng product.detail và làm sạch để không phá vỡ cấu trúc table
        description = product.detail.replace('\n', ' ').replace('|', '') if product.detail else "Không có mô tả"
        
        # Cắt ngắn mô tả nếu quá dài
        short_description = (description[:100] + '...') if len(description) > 100 else description

        product_list_str += f"| {product.name} | {categories} | {price}đ | {short_description} |\n"
        
    return product_list_str

# ==========================
# 🧭 PROMPT HỆ THỐNG (định hướng bot)
# ==========================
def get_base_prompt():
    """
    Tạo prompt hệ thống bằng cách kết hợp thông tin tĩnh và dữ liệu sản phẩm động.
    """
    # Lấy danh sách sản phẩm mới nhất từ database
    dynamic_product_data = get_product_data_for_prompt()

    # Dữ liệu huấn luyện cơ bản
    TRAINING_DATA = f"""
THÔNG TIN CÔNG TY:
- Tên: Shop Giày 6 Anh Em
- Website: https://6anhemstore.vn
- Địa chỉ: 123 Trần Cao Vân , Đà Nẵng
- Hotline: 0905 456 789
- Email: support@6anhemstore.vn
- Giờ làm việc: 8:00 - 21:00 (Thứ 2 - Thứ 6) ; 8:00 - 12:00 (Thứ 7 - Chủ Nhật)

CHÍNH SÁCH:
- Giao hàng toàn quốc, miễn phí với đơn hàng trên 2.000.000đ.
- Đổi trả trong vòng 7 ngày nếu sản phẩm lỗi.
- Bảo hành 12 tháng chính hãng.

HƯỚNG DẪN MUA HÀNG:
- Bạn có thể đặt hàng trực tiếp qua website hoặc nhắn tin cho nhân viên hỗ trợ.
- Thanh toán khi nhận hàng (COD) hoặc chuyển khoản ngân hàng.

DANH SÁCH SẢN PHẨM:
{dynamic_product_data}
"""

    BASE_PROMPT = f"""
Bạn là một trợ lý bán hàng ảo thân thiện và chuyên nghiệp cho website thương mại điện tử của công ty chúng tôi.

Dưới đây là thông tin nền mà bạn cần dùng để trả lời khách hàng:

{TRAINING_DATA}

Nguyên tắc phản hồi:
- Dựa vào DANH SÁCH SẢN PHẨM được cung cấp để tư vấn chi tiết cho khách hàng. Chú ý đến Tên sản phẩm, Danh mục, Giá và Mô tả.
- Nếu người dùng hỏi về thông tin không có trong dữ liệu trên, hãy nói: “Xin lỗi, hiện tôi chưa có thông tin về vấn đề đó.”
- Giữ phong cách thân thiện, lịch sự, chuyên nghiệp và dễ hiểu.
- Tuyệt đối không bịa đặt thông tin.
"""
    return BASE_PROMPT

# ==========================
# 🌐 GIAO DIỆN CHATBOT
# ==========================
def chatbot_view(request):
    return render(request, 'chatbot/chatbot.html')

# ==========================
# 💬 API XỬ LÝ YÊU CẦU NGƯỞI DÙNG
# ==========================
@csrf_exempt
def chatbot_api(request):

    # BẮT BUỘC: tạo session nếu chưa có
    if not request.session.session_key:
        request.session.create()

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip().lower()

        meaningless_inputs = ["", ".", "..", "...", ",", "?", "!", ";", ":", " "]

        if user_message in meaningless_inputs:
            return JsonResponse({
                'reply': '🤔 Bạn hãy nhập câu hỏi để mình hỗ trợ nhé!',
                'show_button': False
            })

        # ⬅️ LẤY LẠI DANH SÁCH SP HOẶC RỖNG
        last_product_list = request.session.get('last_product_list', [])

        print(">> SESSION KEY:", request.session.session_key)
        print(">> LAST PRODUCTS:", last_product_list)

        # ================================
        # XỬ LÝ TIN NHẮN
        # ================================
        if any(k in user_message for k in ["giày", "sản phẩm", "thông tin", "giá", "chi tiết"]):

            base_prompt = get_base_prompt()
            full_prompt = f"{base_prompt}\n\nNgười dùng: {user_message}\nTrợ lý:"

            response = model.generate_content(full_prompt)
            reply = response.text.strip()

            # Tìm sản phẩm user nhắc tới
            mentioned_products = []
            for p in Product.objects.all():
                if p.name.lower() in user_message:
                    mentioned_products.append(p.name)

            # ⬅️ LƯU VÀO SESSION
            if mentioned_products:
                request.session['last_product_list'] = mentioned_products
                request.session.save()

        else:
            base_prompt = get_base_prompt()
            full_prompt = f"{base_prompt}\n\nNgười dùng: {user_message}\nTrợ lý:"

            response = model.generate_content(full_prompt)
            reply = response.text.strip()

        # Lưu lịch sử
        ChatHistory.objects.create(
            user_id=request.session.session_key,
            user_message=user_message,
            bot_reply=reply
        )

        return JsonResponse({'reply': reply})

    return JsonResponse({'error': 'Invalid request'}, status=400)