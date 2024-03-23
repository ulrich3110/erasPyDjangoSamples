import datetime
import os
import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


class zlm_Lotto():
    ''' Lotto-Spiel-Objekt '''

    def __init__(self):
        ''' Initialisieren '''
        # Output, True, False
        self.blOutput = False
        # Dictionairies für Grundlagen, erweiterte Daten, Prognoosen
        self.dcBasicDraw = {}
        self.dcExtData = {}
        self.dcPredDraw = {}
        # Dictionairies für Zufalls-Tipp, Zufalls-Ziehung
        self.dcRandDraw = {}
        self.dcLottoDraw = {}
        # Dictionairy für Context der View
        self.dcContext = {}
        # Zahlen und Zusatz-Zahl in Ziehungen
        self.lsDrawZahlen = [
            'Zahl 1',
            'Zahl 2',
            'Zahl 3',
            'Zahl 4',
            'Zahl 5',
            'Zahl 6'
        ]
        self.lsDrawZusatz = ['Zusatz-Zahl']
        # Spaltennamen Lotto-Ziehungs-Zahlen
        self.lsTxColDraws = [
            'Zahl 1',
            'Zahl 2',
            'Zahl 3',
            'Zahl 4',
            'Zahl 5',
            'Zahl 6',
            'Zusatz-Zahl'
        ]
        # Spaltennamen Lotto-Zahlen
        self.lsTxColDrawZahlen = [
            'Zahl 1',
            'Zahl 2',
            'Zahl 3',
            'Zahl 4',
            'Zahl 5',
            'Zahl 6'
        ]
        # Spaltennamen Lotto-Zusatzzahlen
        self.lsTxColDrawZusatz = ['Zusatz-Zahl']
        # Spaltennamen Voraussage Zahlen
        self.lsTxColPredZahlen = [
            'PredZ1',
            'PredZ2',
            'PredZ3',
            'PredZ4',
            'PredZ5',
            'PredZ6'
        ]
        # Spaltennamen Voraussage Zusatz Zahlen
        self.lsTxColPredZusatz = ['PredZZ']
        # Spaltennamen als Listen: Durchschnitte, Zielzahlen
        self.lsTxColAvgs = [
            'AvgZ1',
            'AvgZ2',
            'AvgZ3',
            'AvgZ4',
            'AvgZ5',
            'AvgZ6',
            'AvgZZ'
        ]
        self.lsTxColTrgs = [
            'TrgZ1',
            'TrgZ2',
            'TrgZ3',
            'TrgZ4',
            'TrgZ5',
            'TrgZ6',
            'TrgZZ'
        ]
        # Evaluations Dictionairy
        self.dcEval = {
            'PRED-ZAHL': [],
            'PRED-ZUSATZ': [],
            'RAND-ZAHL': [],
            'RAND-ZUSATZ': []
        }
        # Generator Objekt
        self.obGen = Generator()
        self.obGen.lsDrawZahlen = self.lsDrawZahlen
        self.obGen.lsDrawZusatz = self.lsDrawZusatz
        # Draws Objekt
        self.obDraw = Draws()
        self.obDraw.lsTxColDraws = self.lsTxColDraws
        self.obDraw.lsTxColAvgs = self.lsTxColAvgs
        self.obDraw.lsTxColTrgs = self.lsTxColTrgs
        # Regression Objekt
        self.obRegr = LogReg()

    def mSetOutput(self):
        ''' Weist allen Objekten den Output Status zu '''
        self.obGen.blOutput = self.blOutput
        self.obDraw.blOutput = self.blOutput
        self.obRegr.blOutput = self.blOutput

    def mSetBasicDraws(self):
        ''' Zufalls Ziehungen ertellen '''
        # Ziehungen erstellen
        self.obGen.mRandomDraws()
        # In Grundlagen Ziehungen übertragen
        self.dcBasicDraw = self.obGen.dcDraw

    def mSetAdditionalDatas(self):
        ''' Grundlagen Ziehungen erwetiern mit Daten '''
        # Zufalls-Ziehungen in erweiterte Daten übertragen
        for txKey, vlValue in self.dcBasicDraw.items():
            self.dcExtData[txKey] = vlValue
        self.obDraw.pdDraws = pd.DataFrame(self.dcExtData)
        # SMA setzen: .pdDraws
        self.obDraw.mSetSma()
        # Ziel Datums-Daten hinzufügen: .pdDraws
        self.obDraw.mSetTrgDates()
        # Ziel Zahlen hinzufügen: .pdDraws
        self.obDraw.mSetTrgNumbers()
        # Zurückführn zu erweiterten Daten
        self.dcExtData = self.obDraw.pdDraws.to_dict('list')

    def mSetLogRegression(self):
        ''' Für alle Zahlen eine logistische Regression machen '''
        # Dictionairy für Ziehungszahlen, Zeitstempel
        self.obGen.mSetDateNow()
        self.dcPredDraw = {'Datum': self.obGen.txDateTime}
        for txKey in self.lsTxColDraws:
            self.dcPredDraw[txKey] = None
        # Alle Ziel-Zahlen durchlaufen nach Index
        for inIdx in range(len(self.lsTxColTrgs)):
            # Ziel-Key & Ziehungs-Key auslesen
            txTargKey = self.lsTxColTrgs[inIdx]
            txDrawKey = self.lsTxColDraws[inIdx]
            # Erweiterte Daten zu obDraw.pdDraw hinzugüen
            self.obDraw.pdDraws = pd.DataFrame(self.dcExtData)
            # Daten auslesen: obDraw.pdData
            self.obDraw.lsCol = [txTargKey, txDrawKey]
            self.obDraw.lsCol.extend(self.lsTxColAvgs)
            # Alle Daten holen mit Werten: obDraw.pdData
            self.obDraw.mGetAll()
            # Zahlen zu Integer: obDraw.pdData
            self.obDraw.mSetInt()
            # Logistische Regression
            self.obRegr.pdBasic = self.obDraw.pdDatas
            self.obRegr.lsX = [txDrawKey]
            self.obRegr.lsX.extend(self.lsTxColAvgs)
            self.obRegr.txY = txTargKey
            self.obRegr.mSetDatas()
            # self.obRegr.mProof()
            self.obRegr.mTrain()
            # Prognose in Ziehung-Dictionairy eintragen
            self.dcPredDraw[txDrawKey] = int(self.obRegr.flPred)

    def mSetRandomReference(self):
        ''' Zufalls-Zahl als Referenz '''
        # Dictionairy für Ziehungszahlen, Zeitstempel
        self.obGen.mSetDateNow()
        self.dcRandDraw = {'Datum': self.obGen.txDateTime}
        for txKey in self.lsTxColDraws:
            self.dcRandDraw[txKey] = None
        # Zufallsziehung
        self.obGen.mSetDraw()
        # Zahlen dem Dictionairy hinzufügen
        inIdx = 0
        for txZahl in self.lsTxColDrawZahlen:
            self.dcRandDraw[txZahl] = self.obGen.lsZahlen[inIdx]
            # Index hochzählen
            inIdx += 1
        # Zusatz Zahlen dem Dictionairy hinzufügen
        inIdx = 0
        for txZusatz in self.lsTxColDrawZusatz:
            self.dcRandDraw[txZusatz] = self.obGen.lsZusatz[inIdx]
            # Index hochzählen
            inIdx += 1
        # Dialog Zufalls-Tipp
        if self.blOutput:
            # Terminal Output, Kontrolle
            print(":: ZLM_LOTTO :: ZUFALLS-TIPP :: dcRandDraw ::")
            print(self.dcRandDraw)

    def mLottoDraw(self):
        ''' Nächste Lotto Ziehung '''
        # Dictionairy für Ziehungszahlen, Zeitstempel
        self.obGen.mSetDateNow()
        self.dcLottoDraw = {'Datum': self.obGen.txDateTime}
        for txKey in self.lsTxColDraws:
            self.dcLottoDraw[txKey] = None
        # Zufallsziehung
        self.obGen.mSetDraw()
        # Zahlen dem Dictionairy hinzufügen
        inIdx = 0
        for txZahl in self.lsTxColDrawZahlen:
            self.dcLottoDraw[txZahl] = self.obGen.lsZahlen[inIdx]
            # Index hochzählen
            inIdx += 1
        # Zusatz Zahlen dem Dictionairy hinzufügen
        inIdx = 0
        for txZusatz in self.lsTxColDrawZusatz:
            self.dcLottoDraw[txZusatz] = self.obGen.lsZusatz[inIdx]
            # Index hochzählen
            inIdx += 1
        # Dialog Lotto-Ziehung
        if self.blOutput:
            # Terminal Output, Kontrolle
            print(":: ZLM_LOTTO :: ZUFALLS-ZIEHUNG :: dcLottoDraw ::")
            print(self.dcLottoDraw)

    def mEvalDraws(self):
        ''' Vergleich der Ziehungen '''
        # Anzahl Richtige für Prognose und Zufallsziehung
        inCorrPredZahl = 0
        inCorrPredZusatz = 0
        inCorrRandZahl = 0
        inCorrRandZusatz = 0
        # Lotto-Ziehung mit Voraussage Zahlen vergleichen
        for txKey in self.lsTxColDrawZahlen:
            # Jede Zahl aus der Ziehung vergleichen
            for txLottoKey in self.lsTxColDrawZahlen:
                if (
                    self.dcPredDraw[txKey] ==
                    self.dcLottoDraw[txLottoKey]
                ):
                    # Richtige Voraussage Zahl
                    inCorrPredZahl += 1
        # Lotto-Ziehung mit Voraussage Zusatz vergleichen
        for txKey in self.lsTxColDrawZusatz:
            # Jeder Zusatz aus der Ziehung vergleichen
            for txLottoKey in self.lsTxColDrawZusatz:
                if (
                    self.dcPredDraw[txKey] ==
                    self.dcLottoDraw[txLottoKey]
                ):
                    # Richtiger Voraussage Zusatz
                    inCorrPredZusatz += 1
        # Lotto-Ziehung mit Zufalls Zahlen vergleichen
        for txKey in self.lsTxColDrawZahlen:
            # Jede Zahl aus der Ziehung vergleichen
            for txLottoKey in self.lsTxColDrawZahlen:
                if (
                    self.dcRandDraw[txKey] ==
                    self.dcLottoDraw[txLottoKey]
                ):
                    # Richtige Zufalls Zahl
                    inCorrRandZahl += 1
        # Lotto-Ziehung mit Zufalls Zusatz vergleichen
        for txKey in self.lsTxColDrawZusatz:
            # Jeder Zusatz aus der Ziehung vergleichen
            for txLottoKey in self.lsTxColDrawZusatz:
                if (
                    self.dcRandDraw[txKey] ==
                    self.dcLottoDraw[txLottoKey]
                ):
                    # Richtiger Zufalls Zusatz
                    inCorrRandZusatz += 1
        # Vergleichs Dictionairy mit Ergebnissen ergänzen
        self.dcEval['PRED-ZAHL'].append(inCorrPredZahl)
        self.dcEval['PRED-ZUSATZ'].append(inCorrPredZusatz)
        self.dcEval['RAND-ZAHL'].append(inCorrRandZahl)
        self.dcEval['RAND-ZUSATZ'].append(inCorrRandZusatz)

    def mAddLottoDraw(self):
        ''' Zufalls Lotto-Ziehung an Grunlagen Ziehungen anhängen '''
        # Datum hinzufügen
        self.dcBasicDraw["Datum"].append(self.dcLottoDraw["Datum"])
        # Zahlen dem Grundlagen-Dictionairy hinzufügen
        inIdx = 0
        for txZahl in self.lsTxColDrawZahlen:
            self.dcBasicDraw[self.lsDrawZahlen[inIdx]].append(
                self.dcLottoDraw[txZahl]
            )
            # Index hochzählen
            inIdx += 1
        # Zusatz Zahlen dem Dictionairy hinzufügen
        inIdx = 0
        for txZusatz in self.lsTxColDrawZusatz:
            self.dcBasicDraw[self.lsDrawZusatz[inIdx]].append(
                self.dcLottoDraw[txZusatz]
            )
            # Index hochzählen
            inIdx += 1
        # Dataframe erzeugen
        pdBasicDraw = pd.DataFrame(self.dcBasicDraw)
        if self.blOutput:
            # Terminal Output, Kontrolle
            print()
            print(":: ZLM_LOTTO :: mAddLottoDraw :: pdBasicDraw ::")
            print(pdBasicDraw)

    def mSetGameViewDict(self):
        '''
        Dictionairy für View
        @ https://erasand.pythonanywhere.com/PYE/unique_id/ZLMgame
        erstellen
        '''
        # Die ersten beiden und die letzten 3 Grundlagen-Ziehungen auslesen
        # Dictionairy für die Übersetzung der Spalten
        dcCol = {
            'Datum': "DT",
            'Zahl 1': "Z1",
            'Zahl 2': "Z2",
            'Zahl 3': "Z3",
            'Zahl 4': "Z4",
            'Zahl 5': "Z5",
            'Zahl 6': "Z6",
            'Zusatz-Zahl': "ZZ"
        }
        # Dictionairy um die Zeilen-Indexe mit dem Key zu verbinden
        dcRow = {
            0: "R1",
            1: "R2",
            -3: "R3",
            -2: "R4",
            -1: "R5"
        }
        # Die ersten beiden und die letzten 3 Zeilen auslesen
        # Keys in Ziehungen durchlaufen
        for txKey in dcCol.keys():
            # ID's der Zeilen durchlaufen
            for inIdx in [0, 1, -3, -2, -1]:
                # Schlüssel für Web-Dictionairy bilden
                txKeyWeb = "{0}_{1}".format(dcRow[inIdx], dcCol[txKey])
                # Wert aus Draws nach Index auslesen
                vlCell = self.dcBasicDraw[txKey][inIdx]
                # Ins Web-Dictidonairy eintragen
                self.dcContext[txKeyWeb] = vlCell
        # ID eintragen, Reihen nach Index durchlaufen
        for inIdx in [0, 1, -3, -2, -1]:
            # Schlüssel für Web-Dictionairy bilden
            txKeyWeb = "{0}_ID".format(dcRow[inIdx])
            # Index auslesen
            txDate = self.dcBasicDraw['Datum'][inIdx]
            inRow = self.dcBasicDraw['Datum'].index(txDate)
            # Ins Web Dictionairy eintragen
            self.dcContext[txKeyWeb] = inRow
        # Prognose eintragen,  Dictionairy für die Übersetzung der Spalten
        dcCol = {
            'Datum': "P_DT",
            'Zahl 1': "P_Z1",
            'Zahl 2': "P_Z2",
            'Zahl 3': "P_Z3",
            'Zahl 4': "P_Z4",
            'Zahl 5': "P_Z5",
            'Zahl 6': "P_Z6",
            'Zusatz-Zahl': "P_ZZ"
        }
        # Keys in Prognose durchlaufen
        for txKey in dcCol.keys():
            # Wert aus Prognose übertragen
            self.dcContext[dcCol[txKey]] = self.dcPredDraw[txKey]
        # Zufalls-Tipp eintragen,  Dictionairy für die Übersetzung der Spalten
        dcCol = {
            'Datum': "Z_DT",
            'Zahl 1': "Z_Z1",
            'Zahl 2': "Z_Z2",
            'Zahl 3': "Z_Z3",
            'Zahl 4': "Z_Z4",
            'Zahl 5': "Z_Z5",
            'Zahl 6': "Z_Z6",
            'Zusatz-Zahl': "Z_ZZ"
        }
        # Keys in Zufalls-Tipp durchlaufen
        for txKey in dcCol.keys():
            # Wert aus Zufalls-Tipp übertragen
            self.dcContext[dcCol[txKey]] = self.dcRandDraw[txKey]
        # Lotto Ziehung eintragen,  Dictionairy für die Übersetzung der Spalten
        dcCol = {
            'Datum': "L_DT",
            'Zahl 1': "L_Z1",
            'Zahl 2': "L_Z2",
            'Zahl 3': "L_Z3",
            'Zahl 4': "L_Z4",
            'Zahl 5': "L_Z5",
            'Zahl 6': "L_Z6",
            'Zusatz-Zahl': "L_ZZ"
        }
        # Keys in Lotto Ziehung durchlaufen
        for txKey in dcCol.keys():
            # Wert aus Lotto Ziehung übertragen
            self.dcContext[dcCol[txKey]] = self.dcLottoDraw[txKey]
        # Vergleich eintragen,  Dictionairy für die Übersetzung der Spalten
        dcCol = {
            'PRED-ZAHL': "V_P_Zs",
            'PRED-ZUSATZ': "V_P_ZZ",
            'RAND-ZAHL': "V_Z_Zs",
            'RAND-ZUSATZ': "V_Z_ZZ"
        }
        # Keys in Vergleich durchlaufen
        for txKey in dcCol.keys():
            # Wert aus Vergleich übertragen
            self.dcContext[dcCol[txKey]] = self.dcEval[txKey][-1]

    def mSetSummaryViewDict(self):
        '''
        Dictionairy für View
        @ https://erasand.pythonanywhere.com/PYE/unique_id/ZLMLsummary
        erstellen
        '''
        # Totale
        inAnzRunden = len(self.dcEval['PRED-ZAHL'])
        inTotPredZahl = sum(self.dcEval['PRED-ZAHL'])
        inTotPredZusatz = sum(self.dcEval['PRED-ZUSATZ'])
        inTotRandZahl = sum(self.dcEval['RAND-ZAHL'])
        inTotRandZusatz = sum(self.dcEval['RAND-ZUSATZ'])
        # Durchschnitte
        flDurPredZahl = inTotPredZahl / float(inAnzRunden)
        flDurPredZusatz = inTotPredZusatz / float(inAnzRunden)
        flDurRandZahl = inTotRandZahl / float(inAnzRunden)
        flDurRandZusatz = inTotRandZusatz / float(inAnzRunden)
        # Context bilden
        self.dcContext = {
            "Anz_Drws": inAnzRunden,
            "R_P_Zs": inTotPredZahl,
            "D_P_Zs": flDurPredZahl,
            "R_P_ZZ": inTotPredZusatz,
            "D_P_ZZ": flDurPredZusatz,
            "R_Z_Zs": inTotRandZahl,
            "D_Z_Zs": flDurRandZahl,
            "R_Z_ZZ": inTotRandZusatz,
            "D_Z_ZZ": flDurRandZusatz
        }


class Generator():
    ''' Lotto Zahlen Generator '''

    def __init__(self):
        ''' Initierung '''
        # Dictionairy mit Zufalls Ziehungen
        self.dcDraw = {}
        # Liste für Zahlen
        self.lsZahlen = []
        # Liste für Zusatz Zahlen
        self.lsZusatz = []
        # Text für Zeitstempel
        self.txDateTime = ""
        # Output, True, False
        self.blOutput = False
        # Zahlen und Zusatz-Zahl in Ziehungen
        self.lsDrawZahlen = []
        self.lsDrawZusatz = []

    def mRandomDraws(self):
        ''' Erstellt Zufallsziehungen '''
        # Dictionairy vorbereiten
        lsColDraws = []
        lsColDraws.extend(self.lsDrawZahlen)
        lsColDraws.extend(self.lsDrawZusatz)
        self.dcDraw = {'Datum': []}
        for txZahl in lsColDraws:
            self.dcDraw[txZahl] = []
        # Anzahl Ziehungen durchlaufen
        if self.blOutput:
            # Terminal Output, Information
            print()
            print(":: ZLM_GENERATOR :: mRandomDraws ::")
        for inDraw in range(1000):
            # Zeitstempel generieren
            self.mSetDateNow()
            # Zufalls-Ziehung machen
            self.mSetDraw()
            # Zeitstempel dem Dicitionairy hinzufügen
            self.dcDraw['Datum'].append(self.txDateTime)
            # Zahlen dem Dictionairy hinzufügen
            inIdx = 0
            for txZahl in self.lsDrawZahlen:
                self.dcDraw[txZahl].append(self.lsZahlen[inIdx])
                # Index hochzählen
                inIdx += 1
            # Zusatz Zahlen dem Dictionairy hinzufügen
            inIdx = 0
            for txZahl in self.lsDrawZusatz:
                self.dcDraw[txZahl].append(self.lsZusatz[inIdx])
                # Index hochzählen
                inIdx += 1
        if self.blOutput:
            # Terminal Output, Kontrolle Dictionairy
            print()
            print(":: ZLM_GENERATOR :: mRandomDraws :: pdDraw ::")
            pdDraw = pd.DataFrame(self.dcDraw)
            print(pdDraw)

    def mSetDateNow(self):
        ''' Erzeugt den aktuellen Zeitstempel '''
        obNow = datetime.datetime.now()
        self.txDateTime = obNow.strftime("%Y-%m-%dT%H:%M:%S.%f")

    def mSetDraw(self):
        ''' Eine Lotto-Ziehung nach Zufall machen '''
        # Anzahl Zahlen und Liste vorbereiten
        inLenZahlen = len(self.lsDrawZahlen)
        self.lsZahlen = []
        # Zahlen durchlaufen
        for inZahl in range(inLenZahlen):
            blLoop = True
            while blLoop:
                inZahl = random.randint(1, 49)
                if inZahl in self.lsZahlen:
                    # Zahl ist brereits vorhanden
                    blLoop = True
                else:
                    # Zahl ist noch nicht vorhanden
                    self.lsZahlen.append(inZahl)
                    blLoop = False
        # Zahlen sortieren
        self.lsZahlen.sort()
        # Anzahl Zusatz Zahlen und Liste vorbereiten
        inLenZusatz = len(self.lsDrawZusatz)
        self.lsZusatz = []
        # Zusatz durchlaufen
        for inZusatz in range(inLenZusatz):
            blLoop = True
            while blLoop:
                inZusatz = random.randint(1, 12)
                if inZusatz in self.lsZusatz:
                    # Zusatz Zahl ist brereits vorhanden
                    blLoop = True
                else:
                    # Zusatz Zahl ist noch nicht vorhanden
                    self.lsZusatz.append(inZusatz)
                    blLoop = False
        # Zusatz Zahlen sortieren
        self.lsZusatz.sort()


class Draws():
    ''' Verwaltung vergangener Ziehungen'''

    def __init__(self):
        ''' Initierung '''
        # Vergangene Ziehungen, Spalten:
        # Datum, Zahl1, Zahl2, Zahl3, Zahl4, Zahl5, Zahl6, Glückszahl
        # AvgZ1, AvgZ2, AvgZ3, AvgZ4, AvgZ5, AvgZ6, AvgGZ,
        # TrgDatum, TrgZ1, TrgZ2, TrgZ3, TrgZ4, TrgZ5, TrgZ6, TrgGZ
        self.pdDraws = None
        # self.txLastDate = ''
        # Spaltennamen als Listen: Ziehungen, Durchschnitte, Zielzahlen
        self.lsTxColDraws = []
        self.lsTxColAvgs = []
        self.lsTxColTrgs = []
        # Dictionairy mit Spaltenliste und Werten
        self.pdDatas = {}
        # Wert aus einem Datenfeld
        self.vlCell = None
        # Grösse der SMA Werte
        self.inSizeSma = 100
        # Dictionairy zum Hinzufügen von Ziehungen
        self.dcAddDraws = {}
        # Output, True, False
        self.blOutput = False

    def mGetAll(self):
        ''' Alle vergangene Ziehungen auslesen '''
        # Alle Spalten auslesen
        self.pdDatas = self.pdDraws[self.lsCol]
        # Leere SMA Werte abtrennen
        self.pdDatas = self.pdDatas[self.inSizeSma - 1:]
        if self.blOutput:
            # Terminal Output, Kontrolle
            print()
            print(":: ZLML_DRAWS :: mGetAll :: pdDatas ::")
            print(self.pdDatas)

    def mSetInt(self):
        ''' Konvertiert alle zu Integer im Wertebreich .pdDatas '''
        # self.pdDatas.options.display.float_format = '{:,.0f}'.format
        # self.pdDatas = self.pdDatas.round(0).astype(int)
        self.pdDatas = self.pdDatas.astype(int)
        if self.blOutput:
            # Terminal Output, Kontrolle
            print()
            print(":: ZLML_DRAWS :: mSetInt :: pdDatas ::")
            print(self.pdDatas)

    def mSetSma(self):
        ''' SMA für jede Ziehung '''
        # Vergangene Ziehungszahlen nach Index durchlaufen
        inLenColDraws = len(self.lsTxColDraws)
        for inIdx in range(inLenColDraws):
            # Keys auslesen
            txDrawKey = self.lsTxColDraws[inIdx]
            txAvgKey = self.lsTxColAvgs[inIdx]
            # SMA erstellen
            self.pdDraws[txAvgKey] = self.pdDraws[txDrawKey].\
                rolling(window=self.inSizeSma).mean()
            # SMA Werte skalieren
            self.pdDraws[txAvgKey] *= self.inSizeSma
            if self.blOutput:
                # Terminal Output, Kontrolle
                print()
                print(":: ZLML_DRAWS :: mSetSma :: pdDraws.{0} ::".format(
                    txDrawKey
                ))
                print(self.pdDraws[txAvgKey])
        if self.blOutput:
            # Terminal Output, Kontrolle
            print()
            print(":: ZLML_DRAWS :: mSetSma :: pdDraws ::")
            print(self.pdDraws)

    def mSetTrgDates(self):
        ''' Ziel Datums-Daten eintragen '''
        # Ziehungsdaten auslesen
        lsDrawDates = self.pdDraws['Datum'].tolist()
        # Liste für Zieldaten
        inLenDrawDates = len(lsDrawDates)
        lsTrgDates = ['-'] * inLenDrawDates
        # Ziehungsdaten nach Index durchlaufen
        for inIdxDraw in range(inLenDrawDates):
            if inIdxDraw < inLenDrawDates - 1:
                # Nächstes Datum existiert, Zieldatum setzen
                lsTrgDates[inIdxDraw] = lsDrawDates[inIdxDraw + 1]
        # Ziehungsdataframe ergänzen
        self.pdDraws['Trg.Datum'] = lsTrgDates
        if self.blOutput:
            # Terminal Output, Kontrolle
            print()
            print(":: ZLML_DRAWS :: mSetTrgDates :: pdDraws ::")
            print(self.pdDraws)

    def mSetTrgNumbers(self):
        ''' Ziel Nummern eintragen '''
        # Vergangene Ziehungszahlen nach Index durchlaufen
        inLenColDraws = len(self.lsTxColDraws)
        for inIdx in range(inLenColDraws):
            # Keys auslesen
            txDrawKey = self.lsTxColDraws[inIdx]
            txTrgKey = self.lsTxColTrgs[inIdx]
            # Ziehungszahlen als Liste
            lsDraws = self.pdDraws[txDrawKey].tolist()
            inLenDraws = len(lsDraws)
            # Liste für Zielzahlen
            lsTrgs = [0] * inLenDraws
            # Ziehungsdaten nach Index durchlaufen
            for inIdxDraw in range(inLenDraws):
                if inIdxDraw < inLenDraws - 1:
                    # Nächste Ziehung existiert, Zielzahl setzen
                    lsTrgs[inIdxDraw] = lsDraws[inIdxDraw + 1]
            # Ziehungsdataframe ergänzen
            self.pdDraws[txTrgKey] = lsTrgs
        if self.blOutput:
            # Terminal Output, Kontrolle
            print()
            print(":: ZLML_DRAWS :: mSetTrgNumbers :: pdDraws ::")
            print(self.pdDraws)


class LogReg():
    ''' Machine Learning mit Logistischer Regression '''

    def __init__(self):
        ''' Initierung '''
        # Basis Daten in einem Pandas Dataframe
        self.pdBasic = None
        # Letzter Tag
        self.pdLast = None
        # Grundlagen, X-Spalten
        self.lsX = []
        # Prognose, Y-Spalte
        self.txY = ''
        # Output, True, False
        self.blOutput = False

    def mSetDatas(self):
        ''' Datenaufbereitung, .pdX und .pdY definieren '''
        # Letzte Zeile als eigenes Dataframe abtrennen
        self.pdLast = self.pdBasic.tail(1)
        # Grundlagen Daten
        self.pdBasic.drop(self.pdLast.index, inplace=True)
        if self.blOutput:
            # Terminal Output, Kontrolle
            print()
            print(":: LOGREG :: GRUNDLAGEN DATEN ::")
            print(self.pdBasic)
            print(":: LOGREG :: LETZTE DATENZEILE ::")
            print(self.pdLast)

    def mProof(self):
        ''' Modell Test trainieren '''
        if self.blOutput:
            # Terminal Output, Kontrolle
            print()
            print(":: LOGREG :: GRUNDLAGEN :: X-Liste ::")
            print(self.lsX)
            print(":: LOGREG :: GESUCHTER WERT :: Y-Text ::")
            print(self.txY)
            print(":: LOGREG :: GRUNDALGEN :: X-Daten ::")
            print(self.pdBasic[self.lsX])
            print(":: LOGREG :: GESUCHTE WERTE :: Y-Daten ::")
            print(self.pdBasic[self.txY])
        # Aufteilen in Trainings und Testdaten: 80/20%
        pdXTrn, pdXTst, pdYTrn, pdYTst = \
            train_test_split(
                self.pdBasic[self.lsX],
                self.pdBasic[self.txY],
                test_size=0.2,
                random_state=42
            )
        # Logistische Regression und Modell Training
        obRegr = LogisticRegression()
        obRegr.fit(pdXTrn, pdYTrn)
        # Genauigkeit und Koeffizient
        obProof = obRegr.predict(pdXTst)
        txScore = str(accuracy_score(pdYTst, obProof))
        # Score Wert als Float
        self.flScore = float(txScore)
        if self.blOutput:
            # Terminal Output, Kontrolle
            print(":: LOGREG :: SCORE ::")
            print(self.flScore)

    def mTrain(self):
        ''' Modell trainieren '''
        if self.blOutput:
            # Terminal Output, Information
            print()
            print(":: LOGREG :: GRUNDLAGEN :: X-Daten ::")
            print(self.pdBasic[self.lsX])
            print(":: LOGREG :: GESUCHTE WERTE :: Y-Daten ::")
            print(self.pdBasic[self.txY])
        # Logistische Regression und Modell Training
        obRegr = LogisticRegression()
        obRegr.fit(
            self.pdBasic[self.lsX],
            self.pdBasic[self.txY]
        )
        # Voraussage
        pdPredictX = self.pdLast[self.lsX]
        obPred = obRegr.predict(pdPredictX)
        # Voraussage als Float
        self.flPred = float(obPred)
        if self.blOutput:
            # Terminal Output, Kontrolle
            print(":: LOGREG :: PROGNOSE ::")
            print(self.flPred)