from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class Vendors(models.Model):
    vend_name = models.CharField(max_length=20)
    vend_address = models.CharField(max_length=50)
    vend_city = models.CharField(max_length=20)
    vend_mobile = models.CharField(max_length=11, validators=[RegexValidator(regex=r'^1[3-9]\d{9}$', message='手机号格式错误')], unique=True)
    intro = models.TextField(blank=True, null=True, verbose_name="供应商简介")
    def __str__(self):
        return self.vend_name
    
class Customers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="关联用户")
    cust_mobile = models.CharField(max_length=11, validators=[RegexValidator(regex=r'^1[3-9]\d{9}$', message='手机号格式错误')], unique=True)
    def __str__(self):
        return self.user.username

class Addresses(models.Model):
    customer = models.ForeignKey('Customers', on_delete=models.CASCADE, related_name='addresses')
    receiver = models.CharField(max_length=20, verbose_name="收货人")
    phone = models.CharField(max_length=11, verbose_name="联系电话")
    province = models.CharField(max_length=20, verbose_name="省")
    city = models.CharField(max_length=20, verbose_name="市")
    district = models.CharField(max_length=20, verbose_name="区/县")
    detail = models.CharField(max_length=100, verbose_name="详细地址")
    is_default = models.BooleanField(default=False, verbose_name="默认地址")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.receiver} - {self.province}{self.city}{self.district}{self.detail}"

class Products(models.Model):
    vendor = models.ForeignKey(Vendors, on_delete=models.PROTECT)
    prod_name = models.CharField(max_length=50)
    prod_price = models.DecimalField(max_digits=10, decimal_places=2)
    prod_detail = models.TextField(blank=True, null=True, verbose_name="商品简介")
    def __str__(self):
        return self.prod_name

class Orders(models.Model):
    customer = models.ForeignKey(Customers,on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
    ('pending', '待支付'),
    ('paid', '已支付'),
    ('shipped', '已发货'),
    ('completed', '已完成'),
    ('cancelled', '已取消'),
]
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    total_amount= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return f"Orders {self.id} by {self.customer.user.username}"
    address = models.ForeignKey('Addresses', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="收货地址")


class OrderItems(models.Model):
    order = models.ForeignKey(Orders, on_delete = models.CASCADE)
    product = models.ForeignKey(Products, on_delete = models.PROTECT)
    quantity = models.PositiveIntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'product'], name='unique_order_product')
        ]
    def __str__(self):
        return f"{self.product.prod_name} x {self.quantity} in order {self.order.id}"

class CartItem(models.Model):
    customer = models.ForeignKey('Customers', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('Products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) 
    class Meta:
        unique_together = ['customer', 'product']   
# Create your models here.
