from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth import get_user_model
from django.utils.text import slugify

# Modell für Kommentare
class Comment(models.Model):
    content = models.TextField(null=True, blank=True)  # Textinhalt des Kommentars, kann leer sein
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE)  # Bezug auf den Benutzer, der den Kommentar geschrieben hat

    def __str__(self):
        return f"{self.user.username} saying {self.content}..."

# Modell für Produkte
class Product(models.Model):
    CATEGORY_CHOICES = (
        ("new", "new"),
        ("cheap", "cheap"),
        ("expensive", "expensive"),
        ("bestseller", "bestseller"),
        ("sale", "sale"),
        ("discount", "discount"),
        ("specialoffer", "specialoffer"),
        ("hot", "hot"),
        ("trending", "trending"),
    )

    name = models.CharField(max_length=100)  # Name des Produkts
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES, default="new")  # Kategorie des Produkts
    image = models.ImageField(upload_to="products/")  # Bild des Produkts
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Preis des Produkts
    quantity = models.IntegerField()  # Menge des Produkts auf Lager
    description = models.TextField()  # Beschreibung des Produkts
    slug = models.CharField(max_length=500, null=True, blank=True)  # URL-freundlicher Name des Produkts
    tags = TaggableManager()  # Tags für das Produkt
    comments = models.ManyToManyField('Comment', blank=True)  # Kommentare zum Produkt

    def __str__(self):
        return self.name

    def update_quantity(self, quantity):
        self.quantity = quantity
        self.save()

    def save(self, *args, **kwargs):
        # Automatisch einen Slug aus dem Namen generieren
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def is_trending(self):
        return self.category == "trending"  # Überprüfen, ob das Produkt in der Kategorie "trending" ist

# Modell für Warenkorbartikel
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Bezug auf das Produkt
    quantity = models.IntegerField()  # Menge des Produkts im Warenkorb

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

# Modell für den Warenkorb
class Cart(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)  # Bezug auf den Benutzer
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Gesamtbetrag des Warenkorbs
    items = models.ManyToManyField(CartItem, blank=True)  # Artikel im Warenkorb

    def __str__(self):
        return f"{self.user.username}'s cart"

    def add_product(self, product, quantity=1):
        # Produkt dem Warenkorb hinzufügen
        cart_item, created = CartItem.objects.get_or_create(product=product, quantity=quantity)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        self.items.add(cart_item)
        self.calculate_total()  # Gesamtbetrag neu berechnen

    def remove_product(self, product):
        # Produkt aus dem Warenkorb entfernen
        cart_item = CartItem.objects.filter(product=product).first()
        if cart_item:
            self.items.remove(cart_item)
            cart_item.delete()
        self.calculate_total()  # Gesamtbetrag neu berechnen

    def calculate_total(self):
        # Gesamtbetrag des Warenkorbs berechnen
        self.total = sum(item.product.price * item.quantity for item in self.items.all())
        self.save()

# Modell für Bestellungen
class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Bezug auf den Benutzer
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)  # Bezug auf den Warenkorb
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")  # Status der Bestellung
    created_at = models.DateTimeField(auto_now_add=True)  # Erstellungsdatum der Bestellung
    updated_at = models.DateTimeField(auto_now=True)  # Aktualisierungsdatum der Bestellung

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def complete_order(self):
        # Bestellung abschließen
        self.status = "completed"
        self.save()

    def cancel_order(self):
        # Bestellung stornieren
        self.status = "cancelled"
        self.save()
