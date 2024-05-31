from rest_framework import serializers
from .models import Product, CartItem, Cart, Order, Comment
from taggit.serializers import (TagListSerializerField, TaggitSerializer)
from cstore.serializers import UserSerializer

# Kommentar Serializer
class CommentSerializer(serializers.ModelSerializer):
    # Verwendet den UserSerializer, um die Benutzerdaten zu serialisieren
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = '__all__'  # Alle Felder des Comment-Modells werden serialisiert

# Produkt Serializer
class ProductSerializer(TaggitSerializer, serializers.ModelSerializer):
    # Tags werden als Liste serialisiert
    tags = TagListSerializerField()
    # Kommentare werden serialisiert, wobei viele Kommentare erlaubt sind
    comments = CommentSerializer(many=True)

    class Meta:
        model = Product
        # Diese Felder des Produktmodells werden serialisiert
        fields = ['id', 'name', 'category', 'image', 'price', 'quantity', 'description', 'tags', 'slug', 'comments']

# Warenkorbartikel Serializer
class CartItemSerializer(serializers.ModelSerializer):
    # Produktdaten werden nur gelesen, nicht bearbeitet
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']  # Diese Felder des CartItem-Modells werden serialisiert

# Warenkorb Serializer
class CartSerializer(serializers.ModelSerializer):
    # Viele CartItems können im Warenkorb sein, nur zum Lesen
    items = CartItemSerializer(many=True, read_only=True)
    # Benutzername des Warenkorbbenutzers wird nur gelesen
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Cart
        # Diese Felder des Warenkorbmodells werden serialisiert
        fields = ['id', 'user', 'total', 'items']

    def create(self, validated_data):
        # Artikel aus den validierten Daten entfernen
        items_data = validated_data.pop('items')
        # Einen neuen Warenkorb erstellen
        cart = Cart.objects.create(**validated_data)
        # Für jeden Artikel im Warenkorb einen CartItem erstellen
        for item_data in items_data:
            CartItem.objects.create(cart=cart, **item_data)
        return cart

    def update(self, instance, validated_data):
        # Artikel aus den validierten Daten entfernen
        items_data = validated_data.pop('items')
        # Den Gesamtbetrag des Warenkorbs aktualisieren
        instance.total = validated_data.get('total', instance.total)
        instance.save()

        # Alle vorhandenen CartItems entfernen und neu erstellen
        instance.items.clear()
        for item_data in items_data:
            CartItem.objects.create(cart=instance, **item_data)

        return instance

# Bestellungs-Serializer
class OrderSerializer(serializers.ModelSerializer):
    # Warenkorbdaten werden nur gelesen
    cart = CartSerializer(read_only=True)
    # Benutzername des Bestellbenutzers wird nur gelesen
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Order
        # Diese Felder des Bestellmodells werden serialisiert
        fields = ['id', 'user', 'cart', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Daten des Warenkorbs aus den validierten Daten entfernen
        cart_data = validated_data.pop('cart')
        # Warenkorb-Serializer erstellen und validieren
        cart_serializer = CartSerializer(data=cart_data)
        cart_serializer.is_valid(raise_exception=True)
        # Warenkorb speichern
        cart = cart_serializer.save()
        # Neue Bestellung mit dem gespeicherten Warenkorb erstellen
        order = Order.objects.create(cart=cart, **validated_data)
        return order

    def update(self, instance, validated_data):
        # Daten des Warenkorbs aus den validierten Daten entfernen
        cart_data = validated_data.pop('cart', None)
        if cart_data:
            # Warenkorb-Serializer mit den neuen Daten aktualisieren und validieren
            cart_serializer = CartSerializer(instance.cart, data=cart_data)
            cart_serializer.is_valid(raise_exception=True)
            cart_serializer.save()

        # Status der Bestellung aktualisieren
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
