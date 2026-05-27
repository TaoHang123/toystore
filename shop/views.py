from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from .models import Vendors, Products, Customers, Orders, OrderItems, CartItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse
from django.db.models import Prefetch
from django.views.decorators.http import require_POST

def index(request):
    products = Products.objects.select_related('vendor').all()
    context = {
        'products': products,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Products.objects.select_related('vendor'),  pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

def vendor_detail(request, pk):
    vendor = get_object_or_404(Vendors.objects.prefetch_related('products_set'), pk=pk)
    products = vendor.products_set.all()  # 反向查询该供应商的所有产品
    return render(request, 'shop/vendor_detail.html', {
        'vendor': vendor,
        'products': products,
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 自动创建一个 Customers 记录，关联到刚创建的用户
            Customers.objects.create(
                user=user,
                cust_mobile=request.POST.get('cust_mobile', ''),
            )
            login(request, user)
            return redirect('shop:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
    
@login_required
def order_list(request):
    customer = request.user.customers
    orders = Orders.objects.filter(customer=customer).order_by('-date')
    return render(request, 'shop/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    # 获取当前用户的 Customers 记录（假设 related_name='customers'）
    customer = request.user.customers
    # 获取订单，同时确保订单属于当前用户
    order = get_object_or_404(
        Orders.objects.select_related('customer')
                     .prefetch_related('orderitems_set__product'),
        id=order_id,
        customer=customer
    )
    # 订单明细已经在 prefetch_related 中预加载
    items = order.orderitems_set.all()
    return render(request, 'shop/order_detail.html', {
        'order': order,
        'items': items,
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, pk=product_id)
    customer = request.user.customers   # 假设 related_name='customers'
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        customer=customer,
        product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    return redirect('shop:cart_detail')
    
@login_required
def cart_detail(request):
    customer = request.user.customers
    cart_items = customer.cart_items.select_related('product').all()
    return render(request, 'shop/cart_detail.html', {'cart_items': cart_items})

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, customer=request.user.customers)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('shop:cart_detail')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, customer=request.user.customers)
    cart_item.delete()
    return redirect('shop:cart_detail')

@login_required
@require_POST
def buy_now(request, product_id):
    product = get_object_or_404(Products, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    # 构造统一的数据结构
    item = {
        'product_id': product.id,
        'name': product.prod_name,
        'price': float(product.prod_price),
        'quantity': quantity,
    }
    # 存入 session（注意是列表）
    request.session['checkout_items'] = [item]
    request.session['checkout_total'] = item['price'] * item['quantity']
    return redirect('shop:confirm_order')

@login_required
def checkout_preview(request):
    if request.method == 'POST':
        selected_ids_str = request.POST.get('selected_ids', '')
        if selected_ids_str:
            selected_ids = [int(x) for x in selected_ids_str.split(',') if x.strip().isdigit()]
        else:
            selected_ids = []
        if not selected_ids:
            return redirect('shop:cart_detail')
        cart_items = CartItem.objects.filter(
            id__in=selected_ids,
            customer=request.user.customers
        ).select_related('product')
        items = []
        total = 0
        for ci in cart_items:
            subtotal = ci.product.prod_price * ci.quantity
            total += subtotal
            items.append({
                'product_id': ci.product.id,
                'name': ci.product.prod_name,
                'price': float(ci.product.prod_price),
                'quantity': ci.quantity,
                # 可选：保留 cart_item_id 供后续删除购物车项
                'cart_item_id': ci.id,
            })
        request.session['checkout_items'] = items
        request.session['checkout_total'] = float(total)
        return redirect('shop:confirm_order')
    return redirect('shop:cart_detail')

def confirm_order(request):
    items = request.session.get('checkout_items')
    total = request.session.get('checkout_total')
    if not items:
        return redirect('shop:product_list')
    return render(request, 'shop/confirm_order.html', {
        'items': items,
        'total': total,
    })

@login_required
def create_order(request):
    if request.method != 'POST':
        return redirect('shop:product_list')
    items_data = request.session.pop('checkout_items', None)
    if not items_data:
        return redirect('shop:product_list')
    customer = request.user.customers
    with transaction.atomic():
        # 获取所有商品 id 列表
        product_ids = [item['product_id'] for item in items_data]
        # 锁定商品行，防止并发修改
        products = Products.objects.select_for_update().filter(id__in=product_ids)
        products_dict = {p.id: p for p in products}
        # 检查所有商品都存在且库存充足（如果有库存字段）
        for item in items_data:
            product = products_dict.get(item['product_id'])
            if not product:
                # 商品不存在，返回错误页面或提示
                return redirect('shop:cart_detail')  # 简易处理
            # 如果有库存字段，可检查
            # if product.stock < item['quantity']: ...
        total = 0
        order = Orders.objects.create(customer=customer, status='pending', total_amount=0)
        for item in items_data:
            product = products_dict[item['product_id']]
            quantity = item['quantity']
            price = product.prod_price  # 使用数据库最新价格（也可以使用 session 中的旧价格，看业务需求）
            subtotal = price * quantity
            total += subtotal
            OrderItems.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                item_price=price,
            )
            # 如果有库存扣减，在此执行：product.stock -= quantity; product.save()
        order.total_amount = total
        order.save()
        # 如果是购物车结算，删除对应的购物车项
        # 注意：需要知道哪些 cart_item_id 要删除
        cart_item_ids = [item.get('cart_item_id') for item in items_data if 'cart_item_id' in item]
        if cart_item_ids:
            CartItem.objects.filter(id__in=cart_item_ids, customer=customer).delete()
    # 清除 session 中的总金额（可选）
    request.session.pop('checkout_total', None)
    return redirect('shop:order_detail', order_id=order.id)
# Create your views here.
