# Structure of RNC .gml file:

.gml for RNC contains the following struct:

```xml
<gml:featureMember>
    <!-- inner featureMember -->
</gml:featureMember>
```

The inner part of the struct can be one of the following 7 features:

```text
RCN_Transakcja, RCN_Dokument, RCN_Nieruchomosc, RCN_Dzialka, RCN_Adres, RCN_Budynek, RCN_Lokal
```

which are related to each other as follows:

```text
RCN_Transakcja -> RCN_Dokument, RCN_Nieruchomosc
RCN_Nieruchomosc -> RCN_Dzialka, RCN_Budynek, RCN_Lokal
RCN_Dzialka -> RCN_Adres
RCN_Budynek -> RCN_Adres
RCN_Lokal -> RCN_Adres
```

# Dependency tree with ids matching the example:

+ RCN_Transakcja

```xml
<rcn:RCN_Transakcja gml:id="RCN_Transakcja.id">
    <!-- inner RCN_Transakcja -->
    <rcn:podstawaPrawna xlink:href="RCN_Dokument_id"/>
    <rcn:nieruchomosc xlink:href="RCN_Nieruchomosc_id"/>
</rcn:RCN_Transakcja>
```

+ RCN_Dokument

```xml
<rcn:RCN_Dokument gml:id="RCN_Dokument_id">
    <!-- inner RCN_Dokument -->
    <!-- no deeper dependencies -->
</rcn:RCN_Dokument>
``` 

+ RCN_Nieruchomosc:

```xml
<rcn:RCN_Nieruchomosc gml:id="RCN_Nieruchomosc_id">
    <!-- inner RCN_Nieruchomosc-->
    <rcn:dzialka xlink:href="RCN_Dzialka_id"/>
    <rcn:budynek xlink:href="RCN_Budynek_id"/>
    <rcn:lokal xlink:href="RCN_Lokal_id"/>
</rcn:RCN_Nieruchomosc>
```

+ RCN_Dzialka:

```xml
<rcn:RCN_Dzialka gml:id="RCN_Dzialka_id">
    <!-- inner RCN_Dzialka-->
    <rcn:adresDzialki xlink:href="RCN_Adres_id"/>
</rcn:RCN_Dzialka>
```

+ RCN_Adres:

```xml
<rcn:RCN_Adres gml:id="RCN_Adres_id">
    <!-- inner RCN_Adres -->
    <!-- no deeper dependencies -->
</rcn:RCN_Adres>
```

+ RCN_Budynek:

```xml
<rcn:RCN_Budynek gml:id="RCN_Budynek_id">
    <!-- inner RCN_Budynek -->
     <rcn:adresBudynku xlink:href="RCN_Adres_id"/>
</rcn:RCN_Budynek>
```

+ RCN_Lokal:

```xml
<rcn:RCN_Lokal gml:id="RCN_Lokal_id">
    <!-- inner RCN_Lokal -->
    <rcn:adresBudynkuZLokalem xlink:href="RCN_Adres_id"/>
</rcn:RCN_Lokal>
```

------------------------------------

# Examples:

RCN_Transakcja:

```xml
<gml:featureMember>
<rcn:RCN_Transakcja gml:id="PL.PZGIK.1465_77777-777_2025-05-14T11-12-57">
<rcn:IdRCN>
<rcn:RCN_IdentyfikatorIIP>
<rcn:przestrzenNazw>PL.PZGiK.5346.RCN</rcn:przestrzenNazw>
<rcn:lokalnyId>77777-777</rcn:lokalnyId>
<rcn:wersjaId>2025-05-14T11:12:57</rcn:wersjaId>
</rcn:RCN_IdentyfikatorIIP>
</rcn:IdRCN>
<rcn:oznaczenieTransakcji>77613</rcn:oznaczenieTransakcji>
<rcn:rodzajTransakcji/>
<rcn:rodzajRynku>1</rcn:rodzajRynku>
<rcn:stronaSprzedajaca>4</rcn:stronaSprzedajaca>
<rcn:stronaKupujaca>4</rcn:stronaKupujaca>
<rcn:cenaTransakcjiBrutto>500000.00</rcn:cenaTransakcjiBrutto>
<rcn:podstawaPrawna xlink:href="PL.PZGiK.5346.RCN_00000-000_2010-09-16T00-00-00"/>
<rcn:nieruchomosc xlink:href="PL.PZGiK.5346.RCN_11111-111_2026-02-11T07-34-24"/>
</rcn:RCN_Transakcja>
</gml:featureMember>
```

RCN_Dokument:

```xml
<gml:featureMember>
<rcn:RCN_Dokument gml:id="PL.PZGiK.5346.RCN_00000-000_2010-09-16T00-00-00">
<rcn:oznaczenieDokumentu>9999/2010</rcn:oznaczenieDokumentu>
<rcn:dataSporzadzeniaDokumentu>2010-06-02</rcn:dataSporzadzeniaDokumentu>
<rcn:tworcaDokumentu>ANNA XYZ</rcn:tworcaDokumentu>
</rcn:RCN_Dokument>
</gml:featureMember>
``` 

RCN_Nieruchomosc:

```xml
<gml:featureMember>
<rcn:RCN_Nieruchomosc gml:id="PL.PZGiK.5346.RCN_11111-111_2026-02-11T07-34-24">
<rcn:rodzajNieruchomosci>4</rcn:rodzajNieruchomosci>
<rcn:rodzajPrawaDoNieruchomosci>3</rcn:rodzajPrawaDoNieruchomosci>
<rcn:udzialWPrawieDoNieruchomosci>1/1</rcn:udzialWPrawieDoNieruchomosci>
<rcn:cenaNieruchomosciBrutto>500000.00</rcn:cenaNieruchomosciBrutto>
<rcn:dzialka xlink:href="PL.PZGiK.5346.RCN_22222-222_2025-05-14T10-58-48"/>
<rcn:budynek xlink:href="PL.PZGiK.5346.RCN_33333-333_2025-05-14T10-58-51"/>
<rcn:lokal xlink:href="PL.PZGiK.5346.RCN_44444-444_2025-05-14T11-00-08"/>
</rcn:RCN_Nieruchomosc>
</gml:featureMember>
```

RCN_Dzialka:

```xml
<gml:featureMember>
<rcn:RCN_Dzialka gml:id="PL.PZGiK.5346.RCN_22222-222_2025-05-14T10-58-48">
<rcn:idDzialki>146519_8.0306.31</rcn:idDzialki>
<rcn:geometria>
<gml:Polygon gml:id="geom.4xxxxxxx-3d77-443a-b698-9912fac192d0" srsName="urn:ogc:def:crs:EPSG::2178">
<gml:exterior>
<gml:LinearRing>
<gml:posList>5791000.00 7498000.00 5791100.00 7498000.00 5791100.00 7498100.00 5791000.00 7498100.00 5791000.00 7498000.00</gml:posList>
</gml:LinearRing>
</gml:exterior>
</gml:Polygon>
</rcn:geometria>
<rcn:polePowierzchniEwidencyjnej uom="m2">8474.00</rcn:polePowierzchniEwidencyjnej>
<rcn:sposobUzytkowania>3</rcn:sposobUzytkowania>
<rcn:adresDzialki xlink:href="PL.PZGiK.5346.RCN_55555-555_2015-08-20T10-28-22"/>
</rcn:RCN_Dzialka>
</gml:featureMember>
```

RCN_Adres:

```xml
<gml:featureMember>
<rcn:RCN_Adres gml:id="PL.PZGiK.5346.RCN_55555-555_2015-08-20T10-28-22">
<rcn:miejscowosc>Warszawa</rcn:miejscowosc>
<rcn:ulica>ulica XYZ</rcn:ulica>
<rcn:numerPorzadkowy>15</rcn:numerPorzadkowy>
</rcn:RCN_Adres>
</gml:featureMember>
<!-- but can be more pointing the same RCN_Adres data (different RCN_Adres_id) -->
<!-- Yes, it's not unified here -->
<gml:featureMember>
<rcn:RCN_Adres gml:id="PL.PZGiK.5346.RCN_66666-666_2021-05-22T22-53-07">
<rcn:miejscowosc>Warszawa</rcn:miejscowosc>
<rcn:ulica>ulica XYZ</rcn:ulica>
<rcn:numerPorzadkowy>15</rcn:numerPorzadkowy>
</rcn:RCN_Adres>
</gml:featureMember>
```

RCN_Budynek:

```xml
<gml:featureMember>
<rcn:RCN_Budynek gml:id="PL.PZGiK.5346.RCN_33333-333_2025-05-14T10-58-51">
<rcn:idBudynku>122222_8.0306.24_BUD</rcn:idBudynku>
<rcn:geometria>
<gml:Polygon gml:id="geom.0ac53776-9b83-4395-82d8-68b6405ca18e" srsName="urn:ogc:def:crs:EPSG::2178">
<gml:exterior>
<gml:LinearRing>
<gml:posList>5791200.00 7498200.00 5791250.00 7498200.00 5791250.00 7498250.00 5791200.00 7498250.00 5791200.00 7498200.00</gml:posList>
</gml:LinearRing>
</gml:exterior>
</gml:Polygon>
</rcn:geometria>
<rcn:rodzajBudynku>110</rcn:rodzajBudynku>
<rcn:adresBudynku xlink:href="PL.PZGiK.5346.RCN_55555-555_2015-08-20T10-28-22"/>
</rcn:RCN_Budynek>
</gml:featureMember>
```

RCN_Lokal:

```xml
<gml:featureMember>
<rcn:RCN_Lokal gml:id="PL.PZGiK.5346.RCN_44444-444_2025-05-14T11-00-08">
<rcn:idLokalu>122222_8.0306.24_BUD.21_LOK</rcn:idLokalu>
<rcn:georeferencja>
<gml:Point gml:id="geom.9e3cf8be-e9f7-4af5-a7ca-587479857d56" srsName="urn:ogc:def:crs:EPSG::2178">
<gml:pos>5791731.17 7498229.06</gml:pos>
</gml:Point>
</rcn:georeferencja>
<rcn:funkcjaLokalu>1</rcn:funkcjaLokalu>
<rcn:liczbaIzb>3</rcn:liczbaIzb>
<rcn:nrKondygnacji>5</rcn:nrKondygnacji>
<rcn:powUzytkowaLokalu uom="m2">54.90</rcn:powUzytkowaLokalu>
<rcn:cenaLokaluBrutto>500000.00</rcn:cenaLokaluBrutto>
<rcn:adresBudynkuZLokalem xlink:href="PL.PZGiK.5346.RCN_66666-666_2021-05-22T22-53-07"/>
</rcn:RCN_Lokal>
</gml:featureMember>
```