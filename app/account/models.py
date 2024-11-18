from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    renter=models.BooleanField(default=False)
    place=models.CharField(max_length=100)
    address=models.TextField()
    status=models.BooleanField(default=False)


class Category(models.Model):
    
    category=models.CharField(max_length=100)
    def __str__(self):
        return self.category
    

class Product(models.Model):

    product_name=models.CharField(max_length=100)
    price=models.PositiveIntegerField()
    image=models.ImageField(upload_to='media',null=True,blank=True)
    description=models.TextField()
    renter=models.ForeignKey(User,on_delete=models.CASCADE)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.product_name


class Order(models.Model):

    start_date = models.DateField()
    end_date = models.DateField()
    quantity = models.PositiveIntegerField()
    address = models.TextField()
    status=models.BooleanField(default=False)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders_as_user')
    renter=models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders_as_renter')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name
    
class Messages(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    message=models.CharField(max_length=100)
    date=models.DateTimeField(auto_now_add=True)
    


class OrderTable(models.Model):
    renter=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    start_date=models.DateField()
    end_date=models.DateField()
    quantity=models.PositiveIntegerField()
   