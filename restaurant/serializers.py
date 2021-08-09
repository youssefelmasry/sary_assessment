from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from rest_framework.serializers import ModelSerializer

from restaurant.models import Reservation, Table, User
from restaurant.helpers import check_if_slots_available

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['employee_number', 'username', 'password']
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_password(self, value):
        validate_password(value)
        return value


    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TableManagementSerializer(ModelSerializer):
    class Meta:
        model = Table
        exclude = ['id']
        ref_name = "Tables"
        
class ReservationSerializer(ModelSerializer):
    table_number = serializers.IntegerField(source='table.table_number')
    
    class Meta:
        model = Reservation
        fields = ['id', 'table_number', 'reserve_start_time', 'reserve_end_time', 'created']
        read_only_fields = ['created', 'id']

    def validate_table_number(self, value):
        if not Table.objects.filter(table_number=value).exists():
            raise serializers.ValidationError(f"Table number {value} does not exist")
        return value

    def create(self, validated_data):
        validated_data.update(validated_data.pop('table'))
        if not check_if_slots_available(**validated_data):
            raise serializers.ValidationError("No reservation available for those time slots")
        validated_data['table'] = Table.objects.get(table_number=validated_data.pop('table_number'))
        return super().create(validated_data)