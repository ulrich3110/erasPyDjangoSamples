from django.test import TestCase
from django.utils import timezone
from PYE24app.models import zlm_Data
from PYE24app.zlm import zlm_Lotto
import pandas as pd
import uuid


class zlmTestCase(TestCase):

    def setUP(self):
        ''' Initialisieren '''
        pass

    def test_zlm_1_draws(self):
        '''
        ZLML :: Backend-Test
        @ https://erasand.pythonanywhere.com/PYE/ZLMdraws
        '''
        print("\n\n")
        print(":" * 70)
        print(":: ZLML TESTCASE :: test_zlm_1_draws ::")
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
        # Ergebnis anzeigen
        print(":: zlm_Data Objekte ::", zlm_Data.objects.all(), "::")
        print(":: ENDE :: test_zlm_1_draws ::")
        print(":" * 70)

    def test_zlm_2_game(self):
        '''
        ZLML :: Backend-Test
        @ https://erasand.pythonanywhere.com/PYE/unique_id/ZLMgame
        '''
        print("\n\n")
        print(":" * 70)
        print(":: ZLML TESTCASE :: test_zlm_2_game ::")
        # Leeres zlm_Data Objekt erstellen
        txUniqueId = str(uuid.uuid4())
        # Lotto Objekt
        obLotto = zlm_Lotto()
        obLotto.blOutput = True
        # Leeres zlm_Data Objekt erzeugen & spechern
        obZlm = zlm_Data(
            created=timezone.now(),
            updated=timezone.now(),
            uniqueId=txUniqueId,
            drawsData=obLotto.dcBasicDraw,
            evalData=obLotto.dcEval
        )
        obZlm.save()
        # Lotto Objekt
        obLotto = zlm_Lotto()
        obLotto.blOutput = True
        obLotto.mSetOutput()
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
            # Ziehung eintragen in Gurundlagen
            obLotto.mAddLottoDraw()
            # Modell speichern mit ergänzten Grundlagen und Vergleich
            obZlm.drawsData = obLotto.dcBasicDraw
            obZlm.evalData = obLotto.dcEval
            obZlm.save()
        # Ergebnis anzeigen
        print(":: blZlm ::", blZlm, "::")
        print(":: zlm_Data Objekte ::", zlm_Data.objects.all(), "::")
        print(":: ENDE :: test_zlm_2_game ::")
        print(":" * 70)



