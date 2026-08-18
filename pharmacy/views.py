from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.utils import timezone 

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import (
    Drug,
    Order,
    OrderItem,
    Sale,
    SaleItem,
)
from .serializers import (
    DrugSerializer,
    OrderSerializer,
    OrderItemSerializer,
    SaleSerializer,
)


# --- HELPER FUNCTIONS ---
def user_has_role(user_id, role_name):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return False

    return user.groups.filter(name=role_name).exists()


# --- DRUG VIEWS ---
@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def drug_list(request):
    if request.method == "GET":
        drugs = Drug.objects.all()
        serializer = DrugSerializer(drugs, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = DrugSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@authentication_classes([])
@permission_classes([AllowAny])
def drug_detail(request, pk):
    try:
        drug = Drug.objects.get(pk=pk)
    except Drug.DoesNotExist:
        return Response({"error": "Drug not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = DrugSerializer(drug)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = DrugSerializer(drug, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        drug.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- ORDER VIEWS ---
@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def order_list(request):
    if request.method == "GET":
        orders = Order.objects.all().order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        order = Order.objects.create()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def add_order_item(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(order=order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@authentication_classes([])
@permission_classes([AllowAny])
def update_order_status(request, order_id):
    supplier_id = request.data.get("supplier")

    if not supplier_id or not user_has_role(supplier_id, "SUPPLIER"):
        return Response(
            {"error": "Supplier access only"}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    allowed_statuses = ["PENDING", "ACCEPTED", "DISPATCHED", "CONFIRMED"]

    if new_status not in allowed_statuses:
        return Response(
            {"error": "Invalid order status"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    order.status = new_status
    order.save()

    return Response(OrderSerializer(order).data)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def confirm_delivery(request, order_id):
    boss_id = request.data.get("boss")

    if not boss_id or not user_has_role(boss_id, "BOSS"):
        return Response(
            {"error": "Boss access only"}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.status != "DISPATCHED":
        return Response(
            {"error": "Order must be dispatched before confirmation"},
            status=status.HTTP_400_BAD_REQUEST
        )

    for item in order.items.all():
        drug = item.drug
        drug.stock_quantity += item.quantity
        drug.save()

    order.status = "CONFIRMED"
    order.save()

    return Response({
        "message": "Delivery confirmed successfully",
        "order": OrderSerializer(order).data
    })


# --- SALE VIEWS ---
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def create_sale(request):
    employee_id = request.data.get("employee")

    if not employee_id or not user_has_role(employee_id, "EMPLOYEE"):
        return Response(
            {"error": "Employee access only"}, 
            status=status.HTTP_403_FORBIDDEN
        )

    drug_id = request.data.get("drug")
    quantity = request.data.get("quantity")

    try:
        employee = User.objects.get(id=employee_id)
        drug = Drug.objects.get(id=drug_id)
    except (User.DoesNotExist, Drug.DoesNotExist):
        return Response(
            {"error": "Employee or drug not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response(
            {"error": "Quantity must be a valid integer"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if drug.stock_quantity < quantity:
        return Response(
            {"error": "Not enough stock"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    sale = Sale.objects.create(employee=employee)

    SaleItem.objects.create(
        sale=sale,
        drug=drug,
        quantity=quantity,
        selling_price=drug.selling_price,
        buying_price=drug.buying_price
    )

    revenue = drug.selling_price * quantity
    cost = drug.buying_price * quantity
    profit = revenue - cost

    sale.total_amount = revenue
    sale.total_profit = profit
    sale.save()

    drug.stock_quantity -= quantity
    drug.save()

    return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def employee_today_sales(request):
    employee_id = request.query_params.get("employee_id")

    if not employee_id:
        return Response({"error": "Employee ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    today = timezone.now().date()

    # Inachukua moja kwa moja kutoka SaleItem kwa ajili ya usalama wa data
    sales_items = SaleItem.objects.filter(
        sale__employee_id=employee_id,
        sale__created_at__date=today
    ).select_related('drug', 'sale').order_by("-sale__created_at")

    sales_data = []
    total_sold_today = 0

    for item in sales_items:
        item_total = float(item.quantity * item.selling_price)
        sales_data.append({
            "id": item.id,
            "drug_name": item.drug.name,
            "quantity": item.quantity,
            "total_price": item_total
        })
        total_sold_today += item_total

    return Response({
        "sales": sales_data,
        "total_sold_today": total_sold_today
    })


# --- AUTHENTICATION API ---
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    groups = user.groups.values_list("name", flat=True)
    role = groups.first() if groups else "NO_ROLE"

    return Response({
        "id": user.id,
        "username": user.username,
        "role": role
    })


# --- DASHBOARD & ANALYTICS VIEWS ---
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def boss_dashboard(request):
    user_id = request.query_params.get("user_id")

    if not user_id or not user_has_role(user_id, "BOSS"):
        return Response(
            {"error": "Boss access only"}, 
            status=status.HTTP_403_FORBIDDEN
        )

    sales_summary = Sale.objects.aggregate(
        total_sales=Sum("total_amount"),
        total_profit=Sum("total_profit")
    )

    total_sales = sales_summary["total_sales"] or 0
    total_profit = sales_summary["total_profit"] or 0
    total_cost = total_sales - total_profit

    low_stock_drugs = Drug.objects.filter(stock_quantity__lte=F("minimum_stock"))
    pending_orders = Order.objects.filter(status="PENDING")
    all_drugs = Drug.objects.all()

    return Response({
        "summary": {
            "total_sales": total_sales,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "low_stock_count": low_stock_drugs.count(),
            "pending_orders_count": pending_orders.count(),
        },
        "low_stock_drugs": DrugSerializer(low_stock_drugs, many=True).data,
        "current_stock": DrugSerializer(all_drugs, many=True).data,
        "pending_orders": OrderSerializer(pending_orders, many=True).data,
    })


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def employee_sales_chart(request):
    employees = User.objects.filter(groups__name="EMPLOYEE")
    labels = []
    sales_data = []

    for emp in employees:
        total = Sale.objects.filter(employee=emp).aggregate(Sum("total_amount"))["total_amount__sum"] or 0
        labels.append(emp.username)
        sales_data.append(total)

    return Response({
        "labels": labels,
        "sales": sales_data
    })


# --- SYSTEM RESET API (BOSS ONLY) ---
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def reset_system_data(request):
    boss_id = request.data.get("boss")

    # Hakikisha aliyetuma ombi ni Boss
    if not boss_id or not user_has_role(boss_id, "BOSS"):
        return Response(
            {"error": "Boss access only! Unauthorized action."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        # Futa data zote za Mauzo na Oda kwenye Database
        SaleItem.objects.all().delete()
        Sale.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        
        # (Hiari) Rudisha stock ya dawa zote kuwa 0
        Drug.objects.all().update(stock_quantity=0)

        return Response({"message": "System data cleared successfully! All sales and orders reset to 0."})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





# --- FRONTEND TEMPLATE VIEWS ---
def login_page(request):
    return render(request, "pharmacy/login.html")


def employee_dashboard_page(request):
    return render(request, "pharmacy/employee-dashboard.html")


def boss_dashboard_page(request):
    return render(request, "pharmacy/boss-dashboard.html")


def supplier_dashboard_page(request):
    return render(request, "pharmacy/supplier-dashboard.html")


def admin_dashboard_page(request):
    return render(request, "pharmacy/admin-dashboard.html")