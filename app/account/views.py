from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from .serializer import *
from rest_framework.response import Response
from rest_framework import permissions, authentication
from .models import *
from rest_framework.decorators import action
from datetime import datetime
from rest_framework import status


class UserCreationView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

class UserDeletionview(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kw):
        user = request.user.id
        User.objects.get(id=user).delete()
        return Response(data='deleted')

class ProductAdd(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    

    def create(self, request, *args, **kw):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.renter:
                category_id = request.data.get('category')
                category = Category.objects.get(id=category_id)
                serializer.save(renter=request.user, category=category)
                return Response(data=serializer.data)
            else:
                return Response('error')
        else:
            return Response(data=serializer.errors)
        
    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        if product:
            if request.user == product.renter:
                product.delete()
                return Response(data='product deleted')
            else:
                return Response(data='only renter can delete')
        else:
            return Response(data='error')
        
    @action(methods=['GET'], detail=False)
    def renter_product(self, request, *args, **kwargs):
        user = request.user
        if user.renter:
            product = Product.objects.filter(renter=user)
            serializer = ProductSerializer(product, many=True)
            return Response(data=serializer.data)
        else:
            return Response(data='error')



class OrderGet(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def list(self, request, *args, **kwargs):
        user = request.user
        if user:
            order = Order.objects.filter(renter=user)
            order_serializer = OrderSerializer(order, many=True)
            return Response(data=order_serializer.data)
        else:
            return Response(data='error')
        
    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user.id == order.user_id:
            order.delete()
            return Response(data='order deleted')
        else:
            return Response(data='error')

class OrderView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            id = kwargs.get('id')
            user = request.user
            product = Product.objects.get(id=id)
            quantity = request.data.get('quantity')
            available = int(product.quantity) - int(quantity)
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            address = request.data.get('address')
            renter = product.renter

            if available >= 0:
                Order.objects.create(user=user, product=product, status=False, quantity=quantity, start_date=start_date, end_date=end_date, address=address, renter=renter)
                return Response(data='ordered')
            else:
                return Response(data='out of stock')
                
        return Response(data='enter valid data')
    
    def put(self, request, *args, **kwargs):
        user = request.user
        id = kwargs.get('id')
        order = Order.objects.get(id=id)

        if user == order.product.renter:
            status = request.data.get('status')
            order.status = status
            order.save()
            if status == '1':
                Messages.objects.create(message='accepted', user=order.user, product=order.product)
            else:
                Messages.objects.create(message='rejected', user=order.user, product=order.product)
                order.delete()

            return Response(data='reacted')
        else:
            return Response(data='error')

class MessageView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user:
            message = Messages.objects.filter(user=user)
            serializer = MessageSerializer(message, many=True)
            return Response(data=serializer.data)

class OrderCustomer(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    



    def list(self, request, *args, **kwargs):
        user = request.user
        if user:
            order = Order.objects.filter(user=user)
            order_serializer = OrderSerializer(order, many=True)
            return Response(data=order_serializer.data)
        else:
            return Response(data='error')



class BookingViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        id = kw.get('id')
        
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."})
        
        bookings = Order.objects.filter(product_id=id)
        booked_dates = []
        total_booked_quantity = 0

        for booking in bookings:
            booked_dates.append({
                'start_date': booking.start_date,
                'end_date': booking.end_date,
                'quantity': booking.quantity
            })
            total_booked_quantity += booking.quantity

        remaining_quantity = product.quantity - total_booked_quantity

        return Response({
            'booked_dates': booked_dates,
            'remaining_quantity': remaining_quantity,
        })
    

class Availability(APIView):
    def post(self, request, *args, **kwargs):
        # Get the product ID from the URL
        id = kwargs.get('id')
        try:
            product = Product.objects.get(id=id)
            renter=product.renter
        except Product.DoesNotExist:
            return Response(data="Product not found")

        # Get all orders for the product
        table = OrderTable.objects.filter(product_id=id)

        # Convert the incoming start and end dates to datetime.date objects
        try:
            current_start = datetime.strptime(request.data.get('start_date'), '%Y-%m-%d').date()
            current_end = datetime.strptime(request.data.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            return Response(data='Invalid date format, should be YYYY-MM-DD')

        # Get current quantity and ensure it's an integer
        try:
            current_quantity = int(request.data.get('quantity'))
        except (ValueError, TypeError):
            return Response(data='Invalid quantity')

        total_quantity = product.quantity  # Total available quantity of the product
        available_quantity = total_quantity  # Initialize with total quantity

        serializer = OrderTableSerializer(data=request.data)
        if serializer.is_valid():
            for item in table:
                item_start = item.start_date
                item_end = item.end_date

                # Check if the requested dates overlap with existing bookings
                if not (current_end < item_start or current_start > item_end):
                    # Dates overlap, so reduce available quantity by the booked quantity
                    available_quantity -= item.quantity
                    if available_quantity < current_quantity:
                        return Response(data='Out of stock: insufficient quantity for the requested dates',status=status.HTTP_400_BAD_REQUEST)

            
            if available_quantity >= current_quantity:
              
                serializer.save(product=product,renter=renter)
                return Response(data='Order added successfully')
            else:
                return Response(data='date conflict',status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors)
    



    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        
        orders = Order.objects.filter(product_id=product_id)
        
        unavailable_dates = []
        total_booked_quantity = 0

        for order in orders:
            unavailable_dates.append({
                'start_date': order.start_date,
                'end_date': order.end_date,
                'quantity': order.quantity,
            })
            total_booked_quantity += order.quantity

        serializer = UnavailableDatesSerializer(unavailable_dates, many=True)
        remaining_quantity = product.quantity - total_booked_quantity

        return Response({
            'booked_dates': serializer.data,
            'remaining_quantity': remaining_quantity,
        }, status=status.HTTP_200_OK)



# admin views

class AdminView(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    serializer_class=UserSerializer
    queryset=User.objects.all()
   
    @action(methods=['GET'], detail=False)
    def get_renter(self, request, *args, **kwargs):
        user=User.objects.filter(renter=1,is_superuser=0)
        user_serializer=UserSerializer(user,many=True)
        return Response(data=user_serializer.data)

    @action(methods=['GET'], detail=False)
    def get_user(self, request, *args, **kwargs):
        user=User.objects.filter(renter=0,is_superuser=0)
        user_serializer=UserSerializer(user,many=True)
        return Response(data=user_serializer.data)
    @action(methods=['POST'], detail=False)
    def category(self, request, *args, **kwargs):
        serializer=CategorySerializer(data=request.data)
        
     
        if serializer.is_valid():
            serializer.save()
            return Response(data='added')
      
    
class Renteraccept(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    serializer_class=UserSerializer
    queryset=User.objects.filter(renter=True)

    def update(self, request, *args, **kwargs):

        instance = self.get_object() 
        serializer = UserSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():  
            status = request.data.get('status')
            if status is not None:
                instance.status = status
            serializer.save()
            return Response(data=serializer.data)
        return Response(serializer.errors, status=400)



class CategoryAddView(viewsets.ModelViewSet):
    

    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    # def create(self, request, *args, **kwargs):
    #     serializer=CategorySerializer(data=request.data)
    #     user=request.user
    #     if user.is_staff:
    #         if serializer.is_valid():
    #           serializer.save()
    #           return Response(data='added')
    #     else:
    #         return Response(data='you have no permission')

class AdminOrderView(APIView):

    def get(self, request, *args, **kwargs):
        id=kwargs.get('id')
        user=User.objects.get(id=id)
        orders = OrderTable.objects.filter(renter=user)
        serializer=OrderTableSerializer(orders,many=True)
        return Response(data=serializer.data)
        

     