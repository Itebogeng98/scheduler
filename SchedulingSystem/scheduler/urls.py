from django.urls import path
from . import views 

urlpatterns = [
    path('accounts/login/', views.login_view, name='login_view'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sales_view/', views.sales_view, name='sales_view'),
    path('vendors_view/', views.vendors_view, name='vendors_view'),
    path('vendors_create/', views.vendors_create, name='vendors_create'),
    path("create_course_view/<int:vendor_id>/", views.create_course_view, name="create_course_view"),
    path("courses_view/<int:vendor_id>/", views.courses_view, name="courses_view"),
    path('import_courses/<int:vendor_id>/', views.import_courses, name='import_courses'),
    path('course/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('course/toggle/<int:course_id>/', views.toggle_course_status, name='toggle_course'),
    path('vendor/edit/<int:vendor_id>/', views.edit_vendor, name='edit_vendor'),
    path('vendor/toggle/<int:vendor_id>/', views.toggle_vendor_status, name='toggle_vendor'),
    path('create_sales/', views.create_sales, name='create_sales'),
    path('client_type_cost_sheet_view/', views.client_type_cost_sheet_view, name='client_type_cost_sheet_view'),
    path('client_type_cost_sheet/<int:client_id>/', views.client_type_cost_sheet, name='client_type_cost_sheet'),
    path("get_costsheet/<int:client_type_id>/<int:course_id>/", views.get_costsheet, name="get_costsheet"),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('sign_up_view/',views.sign_up_view, name='sign_up_view'),
    path('list_sales_for_approval/', views.list_sales_for_approval, name='list_sales_for_approval'),
    path('approve_sale_view/<int:sale_id>/', views.approve_sale_view, name='approve_sale_view'),
    path("sales/<int:sale_id>/approval/", views.approve_or_reject_sale, name="approve_or_reject_sale"),
    path("cost_sheet_view/", views.cost_sheet_view, name="cost_sheet_view"),
    path('ceo_approval_cost_sheet/<int:sheet_id>/', views.ceo_approval_cost_sheet, name='ceo_approval_cost_sheet'),
    path("pending_admins_view/", views.pending_admins_view, name="pending_admins_view"),
    path("approve_admin_view/<int:user_id>/", views.approve_admin_view, name="approve_admin_view"),
    path("decline_admin_view/<int:user_id>/", views.decline_admin_view, name="decline_admin_view"),



    ]
