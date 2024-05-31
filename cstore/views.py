from rest_framework.viewsets import ModelViewSet
from .serializers import UserSerializer
from rest_framework import status, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

# Das User-Modell abrufen
User = get_user_model()

# ViewSet für Benutzerinformationen
class UserView(ModelViewSet):
    serializer_class = UserSerializer  # Serializer, der für diese View verwendet wird
    permission_classes = [permissions.IsAuthenticated]  # Nur authentifizierte Benutzer haben Zugriff

    def get_queryset(self):
        # Gibt den aktuell angemeldeten Benutzer zurück
        user = self.request.user
        return User.objects.filter(id=user.id)

# View zum Erstellen eines neuen Benutzers
class UserCreate(CreateAPIView):
    queryset = get_user_model().objects.all()  # Alle Benutzerobjekte abfragen
    serializer_class = UserSerializer  # Serializer, der für diese View verwendet wird
    permission_classes = []  # Keine Berechtigung erforderlich

    def create(self, request, *args, **kwargs):
        # Benutzerdaten aus der Anfrage abrufen
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        try:
            # Neuen Benutzer erstellen
            user = get_user_model().objects.create(username=username, password=password, email=email)
            user.set_password(password)  # Passwort setzen und hashen
            user.is_active = True  # Benutzer aktivieren
            user.save()  # Benutzer speichern
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            # Fehlermeldung zurückgeben, wenn die Erstellung fehlschlägt
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"status": "error", "content": f"Request failed because {e}", "exists": True})
