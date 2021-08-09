from django.urls import path
from django.urls.conf import include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import routers

from restaurant.views import ReservationViewset, TableDeleteView, UserView, TableListCreateView


restaurant_router = routers.SimpleRouter()

restaurant_router.register("reservation", ReservationViewset, basename="reservation")

urlpatterns = [
    path('user/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/create_employee/', UserView.as_view(), name="create_employee"),
    path('restaurant/tables/', TableListCreateView.as_view(), name="table_management"),
    path('restaurant/tables/<table_number>/', TableDeleteView.as_view(), name="table_management"),
    path('restaurant/', include(restaurant_router.urls)),
]