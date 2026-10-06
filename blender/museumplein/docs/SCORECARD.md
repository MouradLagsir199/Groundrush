# Museumplein-skatepark — bouwlog en cijfers

Doel: elk onderdeel op echte schaal, iteratief tot minimaal een 9.

## Meetbasis (geen cijfer, fundament)

| Bron | Wat | Nauwkeurigheid |
|---|---|---|
| PDOK luchtfoto 2026 (5 cm/px, RD) | Absolute schaal en positie | ±5 cm |
| Drone-foto 03, geregistreerd op PDOK (homografie + ECC) | Plattegrond 2 cm/px | ±10–15 cm t.o.v. PDOK |
| Foto 04 en 05, camera teruggerekend (rms 8 en 4,6 px) | Hoogtes | ±5–10 cm |
| Drone-schuinstand gemeten aan railpaaltjes | Correctie van hoge delen: 0,07/0,25 m per m | — |

Assenstelsel: 1 unit = 1 m, x = oost, y = noord, z = 0 is de straatvloer. Oorsprong RD (120710, 485730).

## P1 — Plattegrond: betonvlak + bakstenen muurkop (2D)

| Iteratie | Wijziging | Randafwijking binnenrand (mediaan / p80) | Cijfer |
|---|---|---|---|
| 1 | GrabCut-contour, bandbreedte per punt | 5 / 14 cm | 6 |
| 2 | Robuuste spline, uitschieters eruit | 5 / 13 cm | 6,5 |
| 3 | Hoeken NW/NE nagetekend, spie bij lantaarnpaal weg | 3 / 7 cm | 8 |
| 4 | Noordband 0,40 m gemeten, opbouw vanaf ruwe contour | 3 / 6 cm | 8,5 |
| 5 | Rimpels bij ledges/borden/kink ZO weggewerkt, render zonder AA | 3 / 11 cm* | **9** |

\* p80 iets hoger door strengere, deterministische meting (meer randpunten); visueel volgen alle randen de foto.
Betonvlak 961 m², inclusief muurkop 1045 m² (OSM: 1058 m²). Hoogte van de muurkop rond de bowl volgt bij de bowl.

## P2 — Oostzijde: ledge L7 + hoepelrail R7

| Iteratie | Wijziging | Controle (foto 04 / foto 05 / bovenaanzicht) | Cijfer |
|---|---|---|---|
| 1 | Ledge 5,39×0,56×0,30 m, rail 0,29 m met 5 hoepels (r 0,22 m) | rail en ledge passen; hoepels ~8 cm verschoven | 8,5 |
| 2 | Hoepels verschoven naar gemeten toppen | hoepels ~5 cm, eindpalen ~5 cm te zuidelijk | 8,5 |
| 3 | Hele rail 4,5 cm noord, stang 0,275 m | rail ±3 cm (04), ±6 cm (05) | 8,5 |
| 4 | Ledge 5,5 cm noord en verlengd tot 5,47 m | ledge-koppen ±5 cm, bovenrand en hoogte kloppen | **9** |

## Correctie meetbasis (na P2)

Camera's van foto 04 en 05 opnieuw berekend met paspunten waarvan de drone-positie voor de schuinstand is gecorrigeerd. Daarna komen trapneuzen uit foto en drone overeen op 0–4 cm (eerder 3–14 cm). P1 en P2 blijven geldig: hun controles in foto 04 vielen binnen dezelfde marge.

## P3a — Trap (4 stootborden), hoepelrail R3, hubba-ledge

| Iteratie | Wijziging | Controle | Cijfer |
|---|---|---|---|
| 1 | Trap uit drone-lijnen, hubba uit drone, R3 uit oude camera | hubba ~0,3 m te kort/oost, R3-voeten 0,1 m te hoog | 6 |
| 2 | Camera's gecorrigeerd; neuzen y@x15 = 11,61/11,23/10,54/10,17 (helling −5,75°), R3 via voeten op bordes/vloer, schuine zijplaat | stootborden en R3 passen; hubba ±0,15 m tussen foto's | 8 |
| 3 | Hubba = gemiddelde van drone en beide foto's | bovenaanzicht 3–5 cm, foto's 5–8 cm | **9** |

## Meetbasis v3 (tijdens P3b)

De foto's zijn perspectief-gecorrigeerd (verticale lijnen staan recht), dus het optische midden ligt ver buiten het beeld. Met een vrij optisch midden in het cameramodel daalt de restfout van foto 04 van 14,5 naar 4,7 px. Foto 04 en 05 geven nu dezelfde hoogtes op ±2 cm (id7-paal 0,918/0,910; L3 0,986/0,983). De trap, R3 en hubba zijn met deze camera's opnieuw gemeten (bovenste traptree 0,46 i.p.v. 0,48).

## P3b — Noordbank, dek, oostbank, hoepelrails R5/R6, bank-ledges L3/L4

| Iteratie | Wijziging | Controle | Cijfer |
|---|---|---|---|
| 1 | Bank uit drone-band, rails/ledges uit drone + foto05 met lineaire randcorrectie | rails 25–38 px verschoven in foto05 (cameramodel) | 6 |
| 2 | Camera's v3 (vrij optisch midden); bank gefit op 23 grondpunten | rails passen, L3 te gebogen, vouw 0,3–0,6 m onzeker | 7,5 |
| 3 | Vouwlijnen uit scherpe licht/donker-rand drone (rms 0,9/2,5 cm); L3 rechte top 0,58→0,99 | rails, L3, vouwen in beide foto's en bovenaanzicht | 8,5 |
| 4 | L4-as gecorrigeerd (80° i.p.v. 83°), gemeten topverloop 0,37→0,70→0,83, dekhoogte per zone (0,43 / 0,46 / 0,42) | L4 ±3 cm bovenaanzicht, ±1 cm foto05 | **9** |

## P4 — Noord-quarterpipe (west / verhoogd middenblok / oost) + copings

| Iteratie | Wijziging | Controle | Cijfer |
|---|---|---|---|
| 1 | Eén hoogteveld (max van 3 secties), middenblok als diepe sectie | blok te diep, gaten en zaagtanden bij de overgangen | 6 |
| 2 | Middenblok = plateau 0,30 m + doorgetrokken helling met top-cap; copings ingekort | silhouet en copings kloppen, kreukels 0,3–0,4 m verkeerd, driehoeken rafelig | 7,5 |
| 3 | Kreukellijnen gemeten in foto05 (randversterkt), QP opgesplitst in 5 regio's met eigen triangulatie en verticale randen; copings geknipt op de rand | silhouet ±1 cm hoogte, kreukels ±0,1–0,15 m, copings 1,33–1,375 / 1,68 / 1,36–1,385 m | **9** |

Profiel uit het silhouet van het oosteinde: hoogte 0,94 m boven dek, diepte 1,70 m (west/oost), middenblok 1,22 m / 2,33 m.

## Controle absolute hoogteschaal (na P4)

Alle hoogtes komen uit foto 04/05. Die foto's zijn perspectief-gecorrigeerd, dus de hoogteschaal leunt op de aanname van vierkante pixels. Onafhankelijke controles:

| Test | Uitkomst |
|---|---|
| Foto 04 vs foto 05 (los gekalibreerd) | zelfde hoogtes ±2 cm (paal 0,918/0,910; L3 0,986/0,983) |
| Foto 06 (tegenoverliggende kant), schaal vrij | factor 1,14–1,27, maar camera-fit matig (rms 11–12 px) |
| Foto 07 (onbewerkte DJI-drone, HFOV 82,5°, rms 3,3 px), silhouetten ledges/rails | beste fit bij factor 0,7–0,85, zwak minimum (schaduwen in het masker) |
| Toilethokje in foto 07 | 2,66–2,88 m (standaard 2,32 m), te klein object voor precisie |
| Baksteenlagen (foto 05) | 55,6 mm per laag: past bij factor 0,94 (Vecht) of 1,08–1,12 (Waal) |

Conclusie: geen eenduidige afwijking. De huidige schaal blijft staan, met ±10–15% onzekerheid in absolute hoogte. **Vastleggen kan met drie metingen met een rolmaat ter plekke**: hoogte stang R7, één stootbord van de trap, hoogte coping noord-QP boven het dek. Alle hoogtes staan in `data/park.json`, dus één schaalfactor past het hele model aan.

## P5 — Funbox (in uitvoering, nog geen cijfer)

- Terrein: kleursegmentatie (vloer/bank/dek) op de drone, dekhoogtes uit stereo (west 0,34, oost 0,57), banks als Laplace-veld. Dekranden geoptimaliseerd tegen stereo: mediaan 3,7 cm afwijking, op de ruisgrens van de stereo.
- Hubba-box gebouwd (2,24 × 0,64 m, top 0,77).
- Nog te doen: dubbele hoepel id16, hoepelrails id14 en id15, brede ledge L-west (id13), en controle in foto 04/05/07 voor een cijfer.

## Nog niet gebouwd

- P6: bowl (eiland, hips, copings, ~2,4 m diep)
- P7: west- en zuidwand (NW-knikledge id4, west-bank), muurkop-hoogtes en zittreden aan de zuid/oostkant
