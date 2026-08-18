from rest_framework import serializers
from .models import (
    Drug,
    Order,
    OrderItem,
    Sale,
    SaleItem,
)


# 1. Drug Serializer
class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = "__all__"


# 2. Order Item & Order Serializers
class OrderItemSerializer(serializers.ModelSerializer):
    drug_name = serializers.CharField(
        source="drug.name",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "drug",
            "drug_name",
            "quantity",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "status",
            "items",
        ]


# 3. Sale Item & Sale Serializers
class SaleItemSerializer(serializers.ModelSerializer):
    drug_name = serializers.CharField(
        source="drug.name",
        read_only=True
    )

    class Meta:
        model = SaleItem
        fields = [
            "id",
            "drug",
            "drug_name",
            "quantity",
            "selling_price",
            "buying_price",
        ]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(
        many=True,
        read_only=True
    )
    employee_name = serializers.CharField(
        source="employee.username",
        read_only=True
    )

    class Meta:
        model = Sale
        fields = [
            "id",
            "employee",
            "employee_name",
            "created_at",
            "total_amount",
            "total_profit",
            "items",
        ]