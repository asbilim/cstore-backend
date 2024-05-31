from django.contrib import admin
from .models import Product, Order, CartItem, Cart

# Eine Liste der Modelle, die im Admin-Bereich registriert werden sollen
models = [Product, Order, CartItem, Cart]

# Jedes Modell in der Liste im Admin-Bereich registrieren
for model in models:
    admin.site.register(model)
    # Das Modell wird im Admin-Bereich sichtbar und verwaltbar
