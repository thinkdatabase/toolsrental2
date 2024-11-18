from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','first_name','last_name','email','username','password','place','address','renter','status','is_superuser']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model=Category
        fields='__all__'
    

class ProductSerializer(serializers.ModelSerializer):
    renter=UserSerializer(read_only=True)
    category=CategorySerializer(read_only=True)

    class Meta:
        model=Product
        fields=['id','product_name','price','image','category','description','renter','quantity']


class OrderSerializer(serializers.ModelSerializer):
   
    user = serializers.CharField(read_only=True)
    product = serializers.CharField(read_only=True)
    date = serializers.DateTimeField(read_only=True)
    status = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'date', 'status', 'start_date', 'end_date', 'quantity', 'address']



class MessageSerializer(serializers.ModelSerializer):
    user=serializers.CharField(read_only=True)
    date=serializers.CharField(read_only=True)
    product=serializers.CharField(read_only=True)

    class Meta:
        model = Messages
        fields = '__all__'

    

class OrderTableSerializer(serializers.ModelSerializer):
    product=serializers.CharField(read_only=True)
    renter=serializers.CharField(read_only=True)

    class Meta:
        model=OrderTable
        fields='__all__'


class UnavailableDatesSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    quantity = serializers.IntegerField()
