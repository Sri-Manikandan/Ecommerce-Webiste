from django.db import models
from django.conf import settings
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200,null=True)
    email = models.CharField(max_length=200,null=True)
    phone = models.CharField(max_length=12,null=True,unique=True)
    def __str__(self):
        return self.name
def get_image_filepath(self, filename):
    return 'product_images/' + str(self.name) + '/product_image.png'
class Product(models.Model):
    name = models.CharField(max_length=200,null=True)
    false_price = models.IntegerField(null=True,blank=False)
    price = models.IntegerField(null=True,blank=False)
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True,blank=True)
    category = models.CharField(max_length=100, null=True)
    def __str__(self):
        return self.name
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
class Order(models.Model):
    status = [('c', 'created'), ('p', 'in progress'), ('d', 'done')]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.CharField(default='c', choices=status, max_length=20)
    transaction_id = models.CharField(max_length=100,null=True)
    def __str__(self):
        return str(self.id)
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,blank=True)
    order  = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True,blank=True)
    quantity = models.IntegerField(default=0 ,null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.order.id)
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True,blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True,blank=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.address
class Improve(models.Model):
    field1 = models.CharField(max_length=400, null=True)
    def __str__(self):
        return self.field1

