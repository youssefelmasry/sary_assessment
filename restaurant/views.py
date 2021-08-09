from datetime import date
from rest_framework.decorators import action
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters


from restaurant.permissions import IsAdminUser
from restaurant.serializers import UserSerializer, TableManagementSerializer, ReservationSerializer
from restaurant import helpers


class UserView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer


class TableListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TableManagementSerializer
    pagination_class = None

    def get_queryset(self):
        return TableManagementSerializer.Meta.model.objects.all()


class TableDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TableManagementSerializer
    lookup_field = 'table_number'

    def get_queryset(self):
        return TableManagementSerializer.Meta.model.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if helpers.is_table_has_reservations(instance):
            return Response({"status": "Cannot delete reserved table"}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReservationViewset(viewsets.GenericViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=ReservationSerializer
    filter_backends = (filters.DjangoFilterBackend, rest_filters.OrderingFilter)
    ordering_fields = ['reserve_start_time', 'reserve_end_time']
    filterset_fields = {'table__table_number': ['exact'], 'created': ['gte', 'lte', 'exact', 'lt', 'gt']}

    def get_queryset(self):
        return ReservationSerializer.Meta.model.objects.all()

    @action(detail=False, methods=['get'])
    def check_available_time_slots(self, request, *args, **kwargs):
        required_seats = request.query_params.get("required_seats")
        if not required_seats:
            return Response({"required_seats": "must provide this parameter in query params"}, status=status.HTTP_400_BAD_REQUEST)
        if not required_seats.isdigit():
            return Response({"required_seats": "must be integer"})
        seats_available = helpers.get_table_with_minimum_number_of_seats(int(required_seats))
        if not seats_available[0]:
            return Response({"status": seats_available[1]}, status=status.HTTP_204_NO_CONTENT)
        return Response(seats_available[1])

    @action(detail=False, methods=['post'])
    def add_reservation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "saved"})

    @action(detail=False, methods=['get'])
    def get_today_reservations(self, request, *args, **kwargs):
        queryset = self.filter_queryset(ReservationSerializer.Meta.model.objects.filter(created=date.today()))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def get_all_reservations(self, request, *args, **kwargs):
        queryset = self.filter_queryset(ReservationSerializer.Meta.model.objects.all())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path="delete_reservation/(?P<pk>[^/.]+)")
    def delete_reservation(self, request, pk=None):
        instance = self.get_object()
        if instance.created != date.today():
            return Response({"status": "Cannot delete reservation in the past"}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)