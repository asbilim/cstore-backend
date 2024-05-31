from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from .views import UserView, UserCreate
from rest_framework.routers import SimpleRouter

# Router für die UserView erstellen
router = SimpleRouter()
router.register('infos', UserView, basename="create-user")

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin-Panel URL
    path('api/auth/login/', TokenObtainPairView.as_view(), name="login"),  # Login-URL für JWT-Token
    path('api/auth/', include(router.urls), name="login"),  # API-Authentifizierungs-URLs
    path('api/auth/create/', UserCreate.as_view(), name="create-user"),  # URL zum Erstellen eines neuen Benutzers
    path("store/", include("store.urls"), name="store"),  # URLs für die Store-Anwendung einbinden
]

# Einstellungen für das Servieren von Medien- und statischen Dateien im Debug-Modus
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
