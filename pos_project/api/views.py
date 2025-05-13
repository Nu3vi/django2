from django.http import Http404
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from rest_framework import mixins
from rest_framework import generics

from api.serializers import ArticuloListSerializer, ArticuloSerializer, ArticuloCreateSerializer, ListaPrecioSerializer, \
    OrdenSerializer
from core.models import Articulo, OrdenCompraCliente


# Create your views here.
@api_view(['GET'])
def articulo_list(request):
    articulos = Articulo.objects.all()
    serializer = ArticuloListSerializer(articulos, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def articulo_detail(request, articulo_id):
    """
     Obtener, actualizar o eliminar un artículo.
     """
    try:
        articulo = Articulo.objects.get(pk=pk)
    except Articulo.DoesNotExist:
        return Response(
            {"error": "Artículo no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )
    if request.method == 'GET':
        serializer = ArticuloSerializer(articulo)
        return Response(serializer.data)
    if request.method == 'GET':
        serializer = ArticuloSerializer(articulo)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ArticuloSerializer(articulo, data=request.data,
                                        partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        articulo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['POST'])
def articulo_create(request):
    """
     Crear un nuevo artículo.
     """
    serializer = ArticuloCreateSerializer(data=request.data)
    if serializer.is_valid():
        articulo = serializer.save()
        return Response(
            ArticuloSerializer(articulo).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticuloListView(APIView):
    """
     Lista todos los artículos o crea uno nuevo.
     """

    def get(self, request, format=None):
        articulos = Articulo.objects.all()
        serializer = ArticuloListSerializer(articulos, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ArticuloCreateSerializer(data=request.data)
        if serializer.is_valid():
            articulo = serializer.save()
            return Response(
                ArticuloSerializer(articulo).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticuloDetailView(APIView):
    """
     Obtener, actualizar o eliminar un artículo.
     """

    def get_object(self, pk):
        try:
            return Articulo.objects.get(pk=pk)
        except Articulo.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        articulo = self.get_object(pk)
        serializer = ArticuloSerializer(articulo)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        articulo = self.get_object(pk)
        serializer = ArticuloSerializer(articulo, data=request.data,
                                        partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        articulo = self.get_object(pk)
        articulo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ArticuloListCreateGeneric(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
     Lista todos los artículos o crea uno nuevo usando mixins.
     """
    queryset = Articulo.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticuloCreateSerializer

        return ArticuloListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Personalizar cómo se guarda el objeto
        articulo = serializer.save()
        # Podríamos hacer más cosas aquí, como logging
class ArticuloDetailGeneric(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    """
     Obtener, actualizar o eliminar un artículo usando mixins.
     """
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class ArticuloListCreateSimple(generics.ListCreateAPIView):
    """
     Lista todos los artículos o crea uno nuevo.
     Versión simplificada con vistas genéricas.
     """
    queryset = Articulo.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticuloCreateSerializer

        return ArticuloListSerializer

class ArticuloDetailSimple(generics.RetrieveUpdateDestroyAPIView):
    """
     Obtener, actualizar o eliminar un artículo.
     Versión simplificada con vistas genéricas.
     """
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer

class ArticuloViewSet(viewsets.ModelViewSet):
    """
    Un viewset para ver y editar artículos.
    """
    queryset = Articulo.objects.all()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]
    filterset_fields = ['grupo', 'linea', 'stock']
    search_fields = ['codigo_articulo', 'descripcion', 'codigo_barras']
    ordering_fields = ['codigo_articulo', 'descripcion', 'stock']

    def get_serializer_class(self):
         if self.action == 'create':
             return ArticuloCreateSerializer
         elif self.action == 'list':
             return ArticuloListSerializer
         return ArticuloSerializer


    @action(detail=True, methods=['get'])
    def precios(self, request, pk=None):
        """
        Endpoint personalizado para obtener precios de un artículo.
        GET /api/articulos/{id}/precios/
        """
        articulo = self.get_object()
        try:
            lista_precio = articulo.listaprecio
            serializer = ListaPrecioSerializer(lista_precio)
            return Response(serializer.data)
        except:
            return Response({"error": "No hay lista de precios"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def bajo_stock(self, request):
        """
        Endpoint personalizado para obtener artículos con bajo stock.
        GET /api/articulos/bajo_stock/
        """
        articulos = Articulo.objects.filter(stock__lt=10)

        serializer = ArticuloListSerializer(articulos, many=True)
        return Response(serializer.data)

class OrdenViewSet(viewsets.ReadOnlyModelViewSet):
    """
     Un viewset para ver órdenes (solo lectura).
     """
    queryset = OrdenCompraCliente.objects.all()
    serializer_class = OrdenSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
         Endpoint para cancelar una orden.
         POST /api/ordenes/{id}/cancelar/
         """
        from pos_project.choices import EstadoOrden
        orden = self.get_object()
        # Solo se pueden cancelar órdenes pendientes
        if orden.estado != EstadoOrden.PENDIENTE:
            return Response(
                {"error": "Solo se pueden cancelar órdenes pendientes."},
                status=status.HTTP_400_BAD_REQUEST
            )

        orden.estado = EstadoOrden.CANCELADA
        orden.save()
        serializer = self.get_serializer(orden)
        return Response(serializer.data)




