
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = csrftoken || getCookie('csrftoken');



var updateBtns = document.getElementsByClassName('update-cart');


for (let i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product;  // Lấy id sản phẩm từ data-product
        var action = this.dataset.action;      // Lấy action từ data-action

        console.log('Product ID:', productId, '| Action:', action);
        console.log('User:', user);

        // Nếu user chưa đăng nhập
        if (user === "AnonymousUser") {
            console.log('⚠️ User chưa đăng nhập — có thể lưu giỏ hàng tạm trong localStorage nếu cần.');
            updateUserOrder(productId, action);  // Gọi luôn hàm cập nhật (tuỳ bạn muốn xử lý localStorage hay không)
        } else {
            console.log('✅ User đã đăng nhập');
            updateUserOrder(productId, action);
        }
    });
}


function updateUserOrder(productId, action) {
    console.log('🔄 Gửi request cập nhật giỏ hàng...');

    var url = '/update_item/';  // URL trong urls.py

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'productId': productId,
            'action': action,
        }),
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then((data) => {
        console.log('✅ Server trả về:', data);

    // Cập nhật số sản phẩm trong giỏ hàng ở biểu tượng giỏ
    if (data.cart_items !== undefined) {
        document.getElementById('cart-total').innerText = data.cart_items;
    }

    // Nếu bạn vẫn muốn reload giỏ hàng riêng (ví dụ trong trang giỏ), có thể xử lý thêm
    if (window.location.pathname === '/cart/') {
        location.reload();
    }
    })
    .catch((error) => {
        console.error('❌ Lỗi khi cập nhật giỏ hàng:', error);
    });
}
