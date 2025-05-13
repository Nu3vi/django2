from rest_framework import serializers
from core.models import Articulo, ListaPrecio, GrupoArticulo, LineaArticulo, ItemOrdenCompraCliente, OrdenCompraCliente


class ArticuloSerializer(serializers.Serializer):
    articulo_id = serializers.UUIDField(read_only=True)
    codigo_articulo = serializers.CharField(max_length=25)
    codigo_barras = serializers.CharField(max_length=25, required=False, allow_blank=True)
    descripcion = serializers.CharField(max_length=150)
    presentacion = serializers.CharField(max_length=100, required=False, allow_blank=True)
    stock = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)

    def create(self, validated_data):
        return Articulo.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.codigo_articulo = validated_data.get('codigo_articulo', instance.codigo_articulo)
        instance.codigo_barras = validated_data.get('codigo_barras', instance.codigo_barras)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.presentacion = validated_data.get('presentacion', instance.presentacion)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.save()
        return instance
class ArticuloModelSerializer(serializers.ModelSerializer):
     class Meta:
         model = Articulo
         fields = ['articulo_id', 'codigo_articulo', 'codigo_barras',
                    'descripcion', 'presentacion', 'stock']
         read_only_fields = ['articulo_id']

class GrupoArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoArticulo
        fields = ['grupo_id', 'codigo_grupo', 'nombre_grupo']

class LineaArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineaArticulo
        fields = ['linea_id', 'codigo_linea', 'nombre_linea']

class ListaPrecioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaPrecio
        fields = ['precio_1', 'precio_2', 'precio_3', 'precio_4',
                  'precio_compra', 'precio_costo']

class ArticuloSerializer(serializers.ModelSerializer):
    grupo = GrupoArticuloSerializer(read_only=True)
    linea = LineaArticuloSerializer(read_only=True)
    # Campo para escribir los IDs
    grupo_id = serializers.UUIDField(write_only=True)
    linea_id = serializers.UUIDField(write_only=True)
    # Incluimos los precios
    precios = ListaPrecioSerializer(source='listaprecio', read_only=True)

    class Meta:
        model = Articulo
        fields = [
            'articulo_id', 'codigo_articulo', 'codigo_barras',
            'descripcion', 'presentacion', 'stock',
            'grupo', 'linea', 'grupo_id', 'linea_id', 'precios'
        ]

    def create(self, validated_data):
        grupo_id = validated_data.pop('grupo_id')
        linea_id = validated_data.pop('linea_id')

        # Obtener objetos reales
        grupo = GrupoArticulo.objects.get(pk=grupo_id)
        linea = LineaArticulo.objects.get(pk=linea_id)

        # Crear el artículo
        articulo = Articulo.objects.create(
            grupo=grupo,
            linea=linea,
            **validated_data
        )

        return articulo

class ArticuloListSerializer(serializers.ModelSerializer):
    grupo_nombre = serializers.CharField(source='grupo.nombre_grupo',
                                         read_only=True)
    linea_nombre = serializers.CharField(source='linea.nombre_linea',
                                         read_only=True)
    precio = serializers.DecimalField(
        source='listaprecio.precio_1',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Articulo
        fields = [
            'articulo_id', 'codigo_articulo', 'descripcion',
            'grupo_nombre', 'linea_nombre', 'stock', 'precio'
        ]

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
     Un ModelSerializer que toma un argumento adicional `fields` que
     controla qué campos deben incluirse.
     """

    def __init__(self, *args, **kwargs):

        # No olvides eliminar 'fields' de kwargs
        fields = kwargs.pop('fields', None)

        # Inicializa como lo harías normalmente
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Elimina todos los campos que no están en la lista de campos
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class ArticuloDynamicSerializer(DynamicFieldsModelSerializer):
    grupo = serializers.SlugRelatedField(slug_field='nombre_grupo',
                                         read_only=True)
    linea = serializers.SlugRelatedField(slug_field='nombre_linea',
                                         read_only=True)

    class Meta:
        model = Articulo
        fields = [
            'articulo_id', 'codigo_articulo', 'codigo_barras',
            'descripcion', 'presentacion', 'grupo', 'linea', 'stock'
        ]

class ItemOrdenSerializer(serializers.ModelSerializer):
    articulo_descripcion = serializers.CharField(source='articulo.descripcion',
                                                 read_only=True)

    class Meta:
        model = ItemOrdenCompraCliente
        fields = [
            'item_id', 'nro_item', 'articulo', 'articulo_descripcion',
            'cantidad', 'precio_unitario', 'total_item'
        ]

class OrdenSerializer(serializers.ModelSerializer):
    items = ItemOrdenSerializer(source='item_orden_compra', many=True,
                                read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombres',
                                           read_only=True)
    estado_display = serializers.CharField(source='get_estado_display',
                                           read_only=True)

    class Meta:
        model = OrdenCompraCliente
        fields = [
            'pedido_id', 'nro_pedido', 'fecha_pedido', 'cliente',
            'cliente_nombre', 'vendedor', 'importe', 'estado',
            'estado_display', 'notas', 'items'
        ]

class ArticuloCreateSerializer(serializers.ModelSerializer):
    grupo_id = serializers.UUIDField()
    linea_id = serializers.UUIDField()
    precio_1 = serializers.DecimalField(max_digits=12, decimal_places=2,
                            min_value=0)

    class Meta:
        model = Articulo
        fields = [
            'codigo_articulo', 'codigo_barras', 'descripcion',
            'presentacion', 'grupo_id', 'linea_id', 'stock', 'precio_1'
        ]

    def validate_codigo_articulo(self, value):
        """
         Validar que el código de artículo sea único.
         """
        if Articulo.objects.filter(codigo_articulo=value).exists():
            raise serializers.ValidationError("Este código de artículo ya existe.")
        return value

    def validate(self, data):
        """
         Validar que la línea pertenezca al grupo.
         """
        grupo_id = data.get('grupo_id')
        linea_id = data.get('linea_id')

        try:
            linea = LineaArticulo.objects.get(pk=linea_id)
            if linea.grupo.grupo_id != grupo_id:
                raise serializers.ValidationError(
                    {"linea_id": "La línea seleccionada no pertenece al grupo."}
                )
        except LineaArticulo.DoesNotExist:
            raise serializers.ValidationError(
                {"linea_id": "La línea seleccionada no existe."}
            )
        return data

    def create(self, validated_data):
        # Extraer precio_1
        precio_1 = validated_data.pop('precio_1')

        # Obtener objetos reales
        grupo_id = validated_data.pop('grupo_id')
        linea_id = validated_data.pop('linea_id')
        grupo = GrupoArticulo.objects.get(pk=grupo_id)
        linea = LineaArticulo.objects.get(pk=linea_id)

        # Generar un UUID para el artículo
        import uuid
        articulo_id = uuid.uuid4()

        # Crear el artículo
        articulo = Articulo.objects.create(
            articulo_id=articulo_id,
            grupo=grupo,
            linea=linea,
            **validated_data
        )

        # Crear lista de precios
        ListaPrecio.objects.create(
            articulo=articulo,
            precio_1=precio_1
        )

        return articulo

