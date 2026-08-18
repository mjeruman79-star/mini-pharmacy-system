from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # A. FRONTEND PAGES (HTML Templates)
    # ==========================================
    # Ukifungua http://127.0.0.1:8000/
    path("", views.login_page, name="login_page"),
    
    # Ukifungua http://127.0.0.1:8000/employee-dashboard/
    path("employee-dashboard/", views.employee_dashboard_page, name="employee_dashboard_page"),
    
    # Ukifungua http://127.0.0.1:8000/boss-dashboard/
    path("boss-dashboard/", views.boss_dashboard_page, name="boss_dashboard_page"),
    
    # Ukifungua http://127.0.0.1:8000/supplier-dashboard/
    path("supplier-dashboard/", views.supplier_dashboard_page, name="supplier_dashboard_page"),
    
    # Ukifungua http://127.0.0.1:8000/admin-dashboard/
    path("admin-dashboard/", views.admin_dashboard_page, name="admin_dashboard_page"),


    # ==========================================
    # B. BACKEND REST APIs (Zote zinaanza na /api/)
    # ==========================================
    
    # --- 1. Authenticaton API ---
    path("api/login/", views.login_api, name="login_api"),

    # --- 2. Drug (Dawa) APIs ---
    path("api/drugs/", views.drug_list, name="drug_list"),  # Kuona dawa zote au kuongeza dawa mpya
    path("api/drugs/<int:pk>/", views.drug_detail, name="drug_detail"),  # Badilisha au futa dawa fulani

    # --- 3. Order (Oda) APIs ---
    path("api/orders/", views.order_list, name="order_list"),  # Leta au tengeneza order mpya
    path("api/orders/<int:order_id>/items/", views.add_order_item, name="add_order_item"),  # Ongeza item kwenye order
    path("api/orders/<int:order_id>/status/", views.update_order_status, name="update_order_status"),  # Supplier kubadili status
    path("api/orders/<int:order_id>/confirm/", views.confirm_delivery, name="confirm_delivery"),  # Boss kuthibitisha delivery

    # --- 4. Sale (Mauzo) APIs ---
    path("api/sales/", views.create_sale, name="create_sale"),  # Fanya mauzo mapya
    path("api/sales/employee-today/", views.employee_today_sales, name="employee_today_sales"),  # Leta mauzo ya leo ya mhudumu huyo tu

    # --- 5. Boss Analytics & Chart APIs ---
    path("api/dashboard/boss/", views.boss_dashboard, name="boss_dashboard"),  # Summary ya Sales, Cost na Profit
    path("api/dashboard/boss/chart/", views.employee_sales_chart, name="employee_sales_chart"),  # Chart ya kulinganisha employees
    path("api/dashboard/boss/reset/", views.reset_system_data, name="reset_system_data"),
]