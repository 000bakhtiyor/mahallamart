from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/<int:id>/', views.shop, name='shop'),
    path('test/', views.itest, name='test'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('apply_promocode/', views.apply_promocode, name='apply_promocode'),
    path('checkout/', views.checkout, name='checkout'),
    path('complete_order/', views.complete_order, name='complete_order'),
    path('search/', views.search, name='search'),
    path('search_api/', views.search_api, name='search_api'),
    path('category/<int:id>/', views.category_detail, name='category_detail'),

    path('control/admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('control/admin/products/', views.admin_products, name='admin_products'),
    path('control/admin/shops/', views.admin_shops, name='admin_shops'),
    path('control/admin/categories/', views.admin_categories, name='admin_categories'),
    path('control/admin/offers/', views.admin_offers, name='admin_offers'),
]