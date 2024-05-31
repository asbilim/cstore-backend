from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CartItemViewSet, CartViewSet, OrderViewSet, AddProductToCartView, RemoveProductFromCartView, AddProductComment

# DefaultRouter erstellen
router = DefaultRouter()
# Routen für ProductViewSet registrieren
router.register(r'products', ProductViewSet)
# Routen für CartItemViewSet registrieren
router.register(r'cart-items', CartItemViewSet)
# Routen für CartViewSet registrieren
router.register(r'carts', CartViewSet)
# Routen für OrderViewSet registrieren
router.register(r'orders', OrderViewSet)

urlpatterns = [
    # Alle Routen des Routers einbinden
    path('', include(router.urls)),
    # Route für das Hinzufügen eines Produkts zum Warenkorb
    path('cart/add_product/', AddProductToCartView.as_view(), name='add_product_to_cart'),
    # Route für das Entfernen eines Produkts aus dem Warenkorb
    path('cart/remove_product/', RemoveProductFromCartView.as_view(), name='remove_product_from_cart'),
    # Route für das Hinzufügen eines Kommentars zu einem Produkt
    path('product/add_comment/', AddProductComment.as_view(), name='add_comment_to_product'),
]
