$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 2,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 4,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 6,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$('.plus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2] 
    $.ajax({
        type:"GET",
        url:"/pluscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity 
            document.getElementById("amount").innerText=data.amount 
            document.getElementById("totalamount").innerText=data.totalamount
        }
    })
})

$('.minus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2] 
    $.ajax({
        type:"GET",
        url:"/minuscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity 
            document.getElementById("amount").innerText=data.amount 
            document.getElementById("totalamount").innerText=data.totalamount
        }
    })
})

// 🗑️ Nút "Hủy" sản phẩm
$(document).on('click', '.remove-cart', function(){
    var id = $(this).attr("pid").toString();
    var eml = this;

    Swal.fire({
        title: 'Xác nhận xóa sản phẩm?',
        text: "Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng không?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Có, xóa!',
        cancelButtonText: 'Không'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                type: "GET",
                url: "/removecart",
                data: { prod_id: id },
                success: function(data){
                    document.getElementById("amount").innerText = data.amount;
                    document.getElementById("totalamount").innerText = data.totalamount;

                    // Xóa hàng khỏi bảng
                    $(eml).closest("tr").fadeOut(400, function(){ $(this).remove(); });

                    // Thông báo toast nhỏ
                    Swal.fire({
                        toast: true,
                        position: 'top-end',
                        icon: 'success',
                        title: 'Đã xóa sản phẩm khỏi giỏ hàng',
                        showConfirmButton: false,
                        timer: 2000
                    });
                }
            });
        }
    });
});





$('.plus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/pluswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            //alert(data.message)
            window.location.href = `http://localhost:8000/product-detail/${id}`
        }
    })
})


$('.minus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/minuswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            window.location.href = `http://localhost:8000/product-detail/${id}`
        }
    })
})