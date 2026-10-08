"""Taches 3, 4, 5 (et bonus) : vues de l'API.

A FAIRE :
  - SalleViewSet (ModelViewSet), avec l'action `occupation` (tache 5)
  - ReservationViewSet (ModelViewSet), avec perform_create (tache 3)
"""
from rest_framework import viewsets  # noqa: F401  (a utiliser)

from .models import Reservation, Salle  # noqa: F401  (a utiliser)

# TODO : votre code ici
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from permissions import IsOwnerOrReadOnly
from serializers import ReservationSerializer
from serializers import serializers


def lire_date(texte):
    if not texte:
        return None
    try:
      d = parse_datetime(texte)
    except ValueError:
        return None
    if d is not None and timezone.is_naive(d):
        d = timezone.make_aware(d)
    return d
  
class SalleViewsSet(viewsets.ModelViewSet):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer
    
    def get_permissions(self):
        if self.action in ("list", "retrieve", "occupation"):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser]
      
@action(detail=True, methods=["get"])
def occupaion(self, request, pk=None):
    salle = self.get_object()
    debut = lire_date(request.query_params.get("debut"))
    fin = lire_date(request.query_params.get("fin"))
    if debut is None or fin is None or fin <= debut:
        return Response(
          {"detail": " date de fin supp à la date de debut"}
          status=400,
        )
        
reservations = Reservation.objects.filter(
  salle=salle,
  statut=Reservation.Statut.CONFIRMEE,
  debut__lt=fin,
  fin__gt=debut,
)

secondes_reservee = 0
for r in reservations:
    d = max(r.debut, debut)
    f = min(r.fin, fin)
    secondes_reservee += (f - d).total_seconds()


duree_periode = (fin - debut).total_seconds()

return Response({
      "salle": salle.id,
      "debut": debut,
      "fin"; fin,
      "taux_occupation": secondes_reservee / duree_periode,
    })