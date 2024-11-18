"""
URL configuration for toolsrental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from account.views import *
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static

router=DefaultRouter()
router.register('user/add',UserCreationView,basename='useradd')
router.register('tools/add',ProductAdd,basename='productadd')
router.register('category/add',CategoryAddView,basename='category')
router.register('user/delete',UserDeletionview,basename='deluser')
router.register('order/view',OrderGet,basename='orderlist')
router.register('order/customer',OrderCustomer,basename='cust')
router.register('renterdet',AdminView,basename='admin')
router.register('renter/accept',Renteraccept,basename='renteracc')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('token/',obtain_auth_token), 
    path('order/<int:id>/',OrderView.as_view(),name='order'),
    path('messages',MessageView.as_view(),name='message'),
    path('bookings/<int:id>/', BookingViewSet.as_view({'get': 'list'})),
    path('ordertable/<int:id>/product',Availability.as_view(),name='available'),
    path('orderadmin/<int:id>/',AdminOrderView.as_view(),name='adminorder'),

   

    

 


    path('products/<int:id>/unavailable-dates/', BookingViewSet.as_view({'get': 'list'}), name='unavailable-dates'),

   

]+router.urls
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
