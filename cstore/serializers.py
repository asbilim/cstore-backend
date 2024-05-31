from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer

# Das User-Modell abrufen
User = get_user_model()

# Serializer für das User-Modell
class UserSerializer(ModelSerializer):
    
    class Meta:
        model = User  # Das Modell, das dieser Serializer verwendet
        fields = ['username', 'password', 'id']  # Felder, die serialisiert werden sollen
        extra_kwargs = {'password': {'write_only': True}}  # Passwortfeld nur zum Schreiben, nicht zum Lesen
