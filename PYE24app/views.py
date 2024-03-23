from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from .models import zlm_Data
from .zlm import zlm_Lotto
import pandas as pd
import uuid


def zlm_index(request):
    # Dictionairy für Template & Rendering
    context = {}
    return render(request, "PYE24app/ZLMindex.html", context)


def zlm_draws(request):
    # Unique ID erzeugen
    txUniqueId = str(uuid.uuid4())
    # Lotto Objekt
    obLotto = zlm_Lotto()
    # Leeres zlm_Data Objekt erzeugen & spechern
    obZlm = zlm_Data(
        created=timezone.now(),
        updated=timezone.now(),
        uniqueId=txUniqueId,
        drawsData=obLotto.dcBasicDraw,
        evalData=obLotto.dcEval
    )
    obZlm.save()
    # Dictionairy für Template & Rendering
    context = {
        # Unique ID
        "UNIQUE_ID": txUniqueId
    }
    return render(request, "PYE24app/ZLMdraws.html", context)


def zlm_game(request, txUniqueId):
    # Lotto Objekt
    obLotto = zlm_Lotto()
    # zlm_Data Objekt laden
    try:
        lsZlm = zlm_Data.objects.filter(uniqueId=txUniqueId)
        obZlm = lsZlm[0]
        blZlm = True
    except zlm_Data.DoesNotExist:
        blZlm = False
    # Prüfen, ob Ojekt gefunden wurde
    if blZlm:
        # Zufalls-Ziehungen übertragen
        obLotto.dcBasicDraw = obZlm.drawsData
        # Vergleich übertragen
        obLotto.dcEval = obZlm.evalData
        # Prüfen, ob dcBasicDraw vorhanden sind
        if not obLotto.dcBasicDraw:
            # Keine Grundlagen vorhanden, erstellen
            obLotto.mSetBasicDraws()
        # Grundlagen erweitern
        obLotto.mSetAdditionalDatas()
        # Logistische Regression
        obLotto.mSetLogRegression()
        # Zufalls-Tipp
        obLotto.mSetRandomReference()
        # Zufalls-Lotto Ziehung
        obLotto.mLottoDraw()
        # Ziehungen vergleichen
        obLotto.mEvalDraws()
        # Dictionairy für View erstellen
        obLotto.dcContext = {"UNIQUE_ID": txUniqueId}
        obLotto.mSetGameViewDict()
        # Ziehuung eintragen in Gurundlagen
        obLotto.mAddLottoDraw()
        # Modell speichern mit ergänzten Grundlagen und Vergleich
        obZlm.drawsData = obLotto.dcBasicDraw
        obZlm.evalData = obLotto.dcEval
        obZlm.updatet = timezone.now()
        obZlm.save()
    # Dictionairy für Template & Rendering
    return render(request, "PYE24app/ZLMgame.html", obLotto.dcContext)


def zlm_summary(request, txUniqueId):
    # Lotto Objekt
    obLotto = zlm_Lotto()
    # zlm_Data Objekt laden
    try:
        lsZlm = zlm_Data.objects.filter(uniqueId=txUniqueId)
        obZlm = lsZlm[0]
        blZlm = True
    except zlm_Data.DoesNotExist:
        blZlm = False
    # Prüfen, ob Ojekt gefunden wurde
    if blZlm:
        # Zufalls-Ziehungen übertragen
        obLotto.dcBasicDraw = obZlm.drawsData
        # Vergleich übertragen
        obLotto.dcEval = obZlm.evalData
        # Dictionairy für View erstellen
        obLotto.dcContext = {"UNIQUE_ID": txUniqueId}
        obLotto.mSetSummaryViewDict()
    # Dictionairy für Template & Rendering
    return render(request, "PYE24app/ZLMsummary.html", obLotto.dcContext)
