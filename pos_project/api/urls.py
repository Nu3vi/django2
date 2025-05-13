
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'articulos', views.ArticuloViewSet, basename='articulo')
router.register(r'ordenes', views.OrdenViewSet, basename='orden')
urlpatterns = [
    path('articulos/', views.articulo_list, name='articulo-list'),
    path('articulos/create/', views.articulo_create, name='articulo-create'),
    path('articulos/<uuid:pk>/', views.articulo_detail, name='articulo-detail'),

    path('articulos/func/', views.articulo_list, name='articulo-list-func'),
    path('articulos/func/create/', views.articulo_create, name='articulo-create-func'),
    path('articulos/func/<uuid:pk>/', views.articulo_detail, name='articulo-detail-func'),

    path('articulos/class/', views.ArticuloListView.as_view(), name='articulo-list-class'),
    path('articulos/class/<uuid:pk>/', views.ArticuloDetailView.as_view(), name='articulo-detail-class'),

    path('articulos/mixins/', views.ArticuloListCreateGeneric.as_view(), name='articulo-list-mixins'),
    path('articulos/mixins/<uuid:pk>/', views.ArticuloDetailGeneric.as_view(), name='articulo-detail-mixins'),

     # Vistas genéricas simplificadas
    path('articulos/generic/', views.ArticuloListCreateSimple.as_view(), name='articulo-list-generic'),
    path('articulos/generic/<uuid:pk>/', views.ArticuloDetailSimple.as_view(), name='articulo-detail-generic'),




]