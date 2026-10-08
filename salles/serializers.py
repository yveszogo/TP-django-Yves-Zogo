"""Tache 1 et 2 : serializers et validation.

A FAIRE :
  - SalleSerializer (ModelSerializer)
  - ReservationSerializer (ModelSerializer) :
      * le champ `utilisateur` est en LECTURE SEULE (il sera renseigne par la vue)
      * validation : `fin` strictement apres `debut`
      * validation : pas de chevauchement avec une autre reservation CONFIRMEE
        de la meme salle
"""
from rest_framework import serializers

from .models import Reservation, Salle  # noqa: F401  (a utiliser)

# TODO : votre code ici
class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = ["id", "nom", "batiment", "capacite"]

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "salle", "utilisateur", "debut", "fin", "motif", "cree_le", "statut"]
        read_only_fields = ["utilisateur", "cree_le"]
        
    def validate(self, data):
        if self.instance:
            debut = data.get("debut", self.instance.debut)
            fin = data.get("fin", self.instance.fin)
            salle = data.get("salle", self.instance.salle)
            statut = data.get("statut", self.instance.statut)
        else:
            debut = data["debut"]
            fin = data["fin"]
            salle = data["salle"]
            statut = data.get("statut", Reservation.Statut.CONFIRMEE)   
            
        if fin <= debut:
            raise serializers.ValidationError("la dete de fin doit etre strictement apres la date de debut.")
          
        if statut == Reservation.Statut.CONFIRMEE:
            conflits = Reservation.objects.filter(
              salle=salle,
              statut=Reservation.Statut.CONFIRMEE,
              debut__lt=fin,
              fin__gt=debut,
            )
            if self.instance:
                conflits = conflits.exclude(pk=self.instance.pk)
            if conflits.exists():
                raise serializers.ValidationError("Cette salle est dejareservee pour cette heure")
              
        return data