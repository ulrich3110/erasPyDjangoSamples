from django.db import models


class zlm_Data(models.Model):
    '''
    ZLM Daten
    - Erstellungs-Datum
    - Letztes Bearbeitungs-Datum
    - Unique ID als Text
    - Vergangene Ziehungen als JSON (Dictionairy)
    - Ergebnisse zum Vergleichen als JSON (Dictionairy)
    '''
    created = models.DateTimeField()
    updated = models.DateTimeField()
    uniqueId = models.CharField(max_length=40)
    drawsData = models.JSONField()
    evalData = models.JSONField()
