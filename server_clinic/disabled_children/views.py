from rest_framework import viewsets
from rest_framework.response import Response
from .models import DisabledChild
from .serializers import DisabledChildSerializer

class DisabledChildViewSet(viewsets.ModelViewSet):
    serializer_class = DisabledChildSerializer
    queryset = DisabledChild.objects.all()
    
    def get_queryset(self):
        policy_number = self.request.query_params.get('policy')
        if policy_number:
            return self.queryset.filter(patient__policy_number=policy_number)
        return self.queryset