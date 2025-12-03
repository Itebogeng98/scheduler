from django.urls import path

from .views import (
    obtain_token,
    vendor_list_create_api,
    create_course_api,
    create_sale_api,
    request_client_type_api,
    cost_sheet_api,
    sale_list_api,
    signup_api,
    approve_sale,
    cost_sheet_list_view_api,
    ceo_approval_cost_sheet_api,
    pending_admins_api,
    approve_admin_api,
    delete_admin_api,
)

urlpatterns = [
    path('obtain_token/', obtain_token, name='obtain_token'),
    path('vendor_list_create_api/', vendor_list_create_api, name='vendor_list_create_api'),
    path("create_course_api/<int:vendor_id>/", create_course_api, name="create_course_api"),
    path("create_sale_api/", create_sale_api, name="create_sale_api"),
    path("request_client_type_api/", request_client_type_api, name="request_client_type_api"),
    path("cost_sheet_api/<int:client_id>/", cost_sheet_api, name="cost_sheet_api"),
    path("sale_list_api/", sale_list_api, name="sale_list_api"),
    path("signup_api/", signup_api, name="signup_api"),
    path("approve_sale/<int:sales_id>/", approve_sale, name="approve_sale"),
    path("cost_sheet_list_view_api", cost_sheet_list_view_api, name="cost_sheet_list_view_api"),
    path("ceo_approval_cost_sheet_api/<int:client_id>/", ceo_approval_cost_sheet_api, name="ceo_approval_cost_sheet_api"),
    path("pending_admins_api/", pending_admins_api , name="pending_admins_api"),
    path("approve_admin_api/<int:user_id>/", approve_admin_api, name="approve_admin_api"),
    path("delete_admin_api/<int:user_id>/", delete_admin_api, name="delete_admin_api"),
]