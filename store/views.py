from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, CartItem, Cart, Order, Comment
from .serializers import ProductSerializer, CartItemSerializer, CartSerializer, OrderSerializer
from rest_framework.views import APIView

# ViewSet für Produkte
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Authentifizierte Benutzer können schreiben, andere nur lesen

# ViewSet für Warenkorbartikel
class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]  # Nur authentifizierte Benutzer können zugreifen

# ViewSet für Warenkörbe
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]  # Nur authentifizierte Benutzer können zugreifen

    def get_queryset(self):
        # Nur den Warenkorb des aktuellen Benutzers zurückgeben
        return Cart.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        # Produkt dem Warenkorb hinzufügen
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)
        cart.add_product(product, quantity)
        return Response({'status': 'product added'})

    @action(detail=True, methods=['post'])
    def remove_product(self, request, pk=None):
        # Produkt aus dem Warenkorb entfernen
        cart = self.get_object()
        product_id = request.data.get('product_id')
        product = Product.objects.get(id=product_id)
        cart.remove_product(product)
        return Response({'status': 'product removed'})

    @action(detail=True, methods=['get'])
    def calculate_total(self, request, pk=None):
        # Gesamtsumme des Warenkorbs berechnen
        cart = self.get_object()
        cart.calculate_total()
        return Response({'total': cart.total})

# ViewSet für Bestellungen
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]  # Nur authentifizierte Benutzer können zugreifen

    def get_queryset(self):
        # Nur Bestellungen des aktuellen Benutzers zurückgeben
        return Order.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete_order(self, request, pk=None):
        # Bestellung abschließen
        order = self.get_object()
        order.complete_order()
        return Response({'status': 'order completed'})

    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        # Bestellung stornieren
        order = self.get_object()
        order.cancel_order()
        return Response({'status': 'order cancelled'})

# APIView zum Hinzufügen eines Produkts zum Warenkorb
class AddProductToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Nur authentifizierte Benutzer können zugreifen

    def post(self, request, *args, **kwargs):
        # Produkt dem Warenkorb hinzufügen
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        try:
            product = Product.objects.get(id=product_id)
            cart.add_product(product, quantity)
            return Response({'status': 'product added'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

# APIView zum Hinzufügen eines Kommentars zu einem Produkt
class AddProductComment(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Nur authentifizierte Benutzer können zugreifen

    def post(self, request, *args, **kwargs):
        # Kommentar zu einem Produkt hinzufügen
        product_id = request.data.get('product_id')
        content = request.data.get('content')

        try:
            product = Product.objects.get(id=product_id)
            comment = Comment.objects.create(user=request.user, content=content)
            product.comments.add(comment)
            product.save()
            return Response({'status': 'comment added'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

# APIView zum Entfernen eines Produkts aus dem Warenkorb
class RemoveProductFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Nur authentifizierte Benutzer können zugreifen

    def post(self, request, *args, **kwargs):
        # Produkt aus dem Warenkorb entfernen
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
            cart.remove_product(product)
            return Response({'status': 'product removed'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
