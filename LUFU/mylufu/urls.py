from django.urls import path

from mylufu.views import *


urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path("branch/", Branch_ListView.as_view(), name="branch_list"),
    path("branch/<int:pk>/", Branch_detailView.as_view(), name="branch_detail"),
    path('register/', RegisterView.as_view(), name='register'),
    path('branch/<int:pk>/menu/', BranchMenuView.as_view(), name='branch_menu'),
    path('branch/<int:pk>/menu/add/', AddMenuView.as_view(), name='add_menu'),
    path('menu/<int:pk>/edit/', EditMenuView.as_view(), name='edit_menu'),
    path('menu/<int:pk>/delete/', DeleteMenuView.as_view(), name='delete_menu'),
    path('branch/<int:branch_id>/menu/order/', OrderSummaryView.as_view(), name='order_summary'),
    path('branch/<int:branch_id>/view_orders/', ViewOrdersView.as_view(), name='view_orders'),
    path('report/', RevenueReportView.as_view(), name='revenue_report'),
]