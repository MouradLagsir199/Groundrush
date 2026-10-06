# Aggressive inline-skategame — volledig concept

Versie: 1.1  
Datum: 6 oktober 2026 (versie 1.0: 29 september 2026)  
Status: concept vastgelegd; de game is nog niet gebouwd of gepubliceerd.  
Projectnaam: nog te kiezen.

Dit document legt de gemaakte keuzes uit het ontwerpoverleg vast en werkt ze uit tot een samenhangend spelconcept. **Vastgesteld** betekent expliciet gekozen of goedgekeurd door de gebruiker. **Voorstel** betekent een verdere ontwerpuitwerking die nog kan veranderen. **Open** betekent dat een besluit, onderzoek of praktijktest nodig is.

Dit is een zelfstandig gameconcept, geen onderdeel van de Prakkie-app of de andere Prakkie-repositories.

**Wijziging in versie 1.1 (vastgesteld):** het skatepark op het Museumplein in Amsterdam vervangt Area 51 in Eindhoven als een van de drie echte parken voor Park Runs. Discovery blijft onderdeel van de eerste release, maar wordt later in de bouwvolgorde gebouwd.

## 1. Het spel in één alinea

Een mobiele aggressive inline-skategame waarin je met een eigen personage op realistische skates door herkenbare locaties rijdt. In **Discovery** verken je Amsterdam centrum, ontdek je spots en uitrusting en ontmoet je reagerende NPC's. In **Park Runs** skate je runs van 90 seconden in exact nagebouwde echte parken in Amsterdam (Museumplein), Barcelona en New York. Je verbetert je scores, bekijkt replays van anderen en ontmoet de community in de parkchat. Je speelt XP, coins, uitrusting en nieuwe parken vrij. Alle bewegingen bedien je met twee duimen: links sturen, rechts springen en tricks kiezen via één touchpad.

## 2. Vastgestelde uitgangspunten

| Onderdeel | Besluit |
| --- | --- |
| Platforms | Android en iOS tegelijk uitbrengen. |
| Presentatie | Horizontale gameplay; 16:9 is het uitgangspunt voor de visuals. |
| Sport | Aggressive inline skating; geen skateboardgame. |
| Gevoel | Realistisch skaten en herkenbare, correct uitgevoerde tricks. |
| Besturing | Linker joystick en één rechter touchpad; geen aparte springknop. |
| Eerste release | Zowel Discovery als Park Runs. |
| Discoverylocatie | Amsterdam centrum, aansluitend op het Museumplein. |
| Discoverypersonages | NPC's die reageren en opdrachten kunnen geven. |
| Eerste drie parken | Museumplein — Amsterdam; Forum — Barcelona; Pier 62 — New York. |
| Nabouw | Echte locaties exact nabouwen, inclusief omgeving, graffiti en aankleding. |
| Runlengte | 90 seconden. |
| Sociale laag | Openbare parkchat vóór en na runs; blokkeren en rapporteren. |
| Speelwereld | Je skate je eigen sessie; geen gedeelde wereld met live rondrijdende menselijke spelers in de huidige scope. |
| Personage | Een eigen skater maken; later meer uiterlijk en uitrusting ontgrendelen. |
| Progressie | XP voor niveau en toegang; verdiende coins voor uitrusting en kleding. |
| Coins | Alleen verdienen door spelen; geen coins met echt geld kopen. |
| Aankopen | Cosmetische items rechtstreeks kopen; later eventueel extra parkpakketten. |
| Basisparken | Alle drie door spelen bereikbaar; geen verplichte aankoop. |
| Ontgrendelen | Een combinatie van speeltijd/voortgang en vaardigheid. |
| Previews | Vergrendelde parken bekijken, inclusief beschikbare runs/replays. |
| Replays | In de game bekijken via het leaderboard, met tricknamen en scoreopbouw. |

De eerdere ideeën voor pc als eerste platform, een live gedeelde discoverywereld, Sydney als startstad en aparte knoppen voor springen en tricks zijn hiermee vervangen. In versie 1.1 is ook Area 51 (Eindhoven) als startpark vervangen door het Museumplein.

## 3. Kern van de spelervaring

### 3.1 Beter worden is de belangrijkste beloning

De speler moet merken dat timing, lijnkeuze, variatie en uitvoering verbeteren. Een zeldzame skate levert geen gratis scorebonus op. De reden om opnieuw te spelen is een trick beter landen, een creatievere lijn ontdekken of een eigen record verbeteren.

### 3.2 Twee modi, één personage

Discovery en Park Runs delen het personage, de garderobe, coins, XP en ontgrendelingen. Discovery levert verkenning, opdrachten en oefening; Park Runs levert gestructureerde uitdagingen en meetbare prestaties.

### 3.3 Zelf skaten, samen een scene vormen

De skatewereld is lokaal. Het sociale contact vindt plaats in de parkcommunity: berichten, profielen, scores en replays. Een speler in de chat hoeft niet op dat moment een run te rijden. NPC's zijn duidelijk te onderscheiden van echte accounts.

## 4. Besturing met twee duimen

### 4.1 Linkerduim: bewegen

- Een grote witte virtuele joystick linksonder stuurt de skater.
- **Voorstel:** vooruit duwen laat de skater afzetten, loslaten laat hem uitrollen en achteruit trekken remt af. De precieze snelheidsregeling moet worden getest.
- De camera volgt de skater zodat een tweede camerajoystick niet verplicht is.
- **Voorstel:** de joystick krijgt in de lucht een functie voor het sturen van rotatie, met duidelijke grenzen om onbedoelde spins te voorkomen.

### 4.2 Rechterduim: één pad voor springen en tricks

| Stap | Gebaar | Resultaat |
| --- | --- | --- |
| 1 | Indrukken en vasthouden | Skater bukt en bereidt de sprong voor. |
| 2 | Tijdens vasthouden vanuit het midden slepen | Richting selecteert een trick; naam of icoon toont de keuze. |
| 3 | Loslaten | Skater springt en probeert de geselecteerde trick. |
| 4 | Tijdens een grind opnieuw indrukken en slepen | Een andere grindpositie selecteren en een overgang proberen. |

De speler hoeft zijn rechterduim nooit snel tussen een springknop en een aparte trickknop te verplaatsen. De twee eerdere conceptbeelden staan onderaan dit document; alleen het tweede sluit aan op de gekozen één-padbediening.

### 4.3 Veel tricks zonder veel knoppen

**Voorstel voor de verdere uitwerking:**

1. Begin met acht richtingen voor een beperkte, consequent ingedeelde set basistricks.
2. Laat de context bepalen welke categorie beschikbaar is: bij een rail/ledge grinds, in een geschikte luchtsituatie grabs.
3. Voeg pas na goede tests gebogen gebaren of twee opeenvolgende richtingen toe voor varianten.
4. Combineer trickkeuze met aanrijrichting, rotatie en overgangen voor complexere lijnen.
5. Toon tijdens het kiezen steeds wat de game heeft herkend. Een richting moet bij gelijke context hetzelfde opleveren.

De exacte gebaren en tricktoewijzing staan nog niet vast. Het systeem mag geen honderden varianten beloven voordat blijkt dat ze betrouwbaar met één duim te bedienen zijn.

### 4.4 Realisme en hulp

- Houdingen, grindcontact, momentum en landingen moeten geloofwaardig zijn.
- Lichte grindhulp helpt beginners bij het leren raken van rails.
- Een moeilijkere competitie zonder of met minder hulp krijgt een aparte ranglijst.
- **Voorstel:** noem de presets voorlopig `Assisted` en `Technical`; definitieve namen volgen.
- Scores van verschillende hulppresets worden niet rechtstreeks gemengd.
- Kantelen voor balans blijft een optionele onderzoeksrichting, met touchalternatief. Schudden is geen verplichte besturing.

### 4.5 Nog te testen bedieningsdetails

Een kale sprong zonder trick, annuleren van een selectie, afspringen uit een grind, fakie rijden, switchhouding, opnieuw positioneren en cameraherstel moeten elk een eenvoudige bediening krijgen. Ze mogen niet stilzwijgend extra gelijktijdige vingers vereisen.

## 5. Spelmodus Discovery

### 5.1 Wereld en schaal

**Vastgesteld:** Amsterdam centrum, herkenbare skateplekken en reagerende NPC's.

De exacte kaartgrens is nog open. De bedoeling is niet automatisch de volledige stad Amsterdam. Het skatepark op het Museumplein is een Park Runs-park (zie hoofdstuk 7). **Voorstel:** de Discoverywereld sluit op het Museumplein aan, zodat het park een herkenbaar ankerpunt in de stad wordt.

### 5.2 Wat de speler doet

- Vrij rondskaten, routes verkennen en nieuwe streetspots ontdekken.
- Oefenen zonder timer of verplichte scorejacht.
- Verborgen onderdelen, kleding en complete skates vinden.
- Opdrachten van NPC's uitvoeren.
- XP en coins verdienen en voortgang meenemen naar Park Runs.
- Ontdekte spots opslaan in een eigen overzicht.

### 5.3 NPC's die reageren

**Vastgesteld:** NPC's zijn meer dan decor; ze reageren op de speler.

**Voorstel voor hun rollen:**

| NPC-type | Functie | Voorbeeld van een reactie |
| --- | --- | --- |
| Lokale skater | Tips, introductie van een spot, trickopdrachten | Reageert wanneer een gevraagde grind lukt. |
| Mentor | Helpt na herhaalde mislukte pogingen | Geeft één gerichte tip over aanloop of timing. |
| Filmer | Vraagt om een specifieke lijn | Wil een bepaalde combinatie op één spot zien. |
| Shopmedewerker | Introduceert uitrusting en onderdelen | Herkent een voltooide opdracht en overhandigt een beloning. |
| Omstanders | Maken de omgeving levendig | Kijken op of stappen opzij wanneer dat logisch is. |

Voor de eerste versie zijn vooraf geschreven dialogen en spelgebeurtenissen het voorstel. Vrije AI-gesprekken of een betaalde AI-dienst per dialoog zijn niet afgesproken.

### 5.4 Opdrachten en beloningen

**Voorbeelden, nog geen definitieve missielijst:**

- Ontdek drie verschillende spots.
- Land een gecontroleerde grind op een aangewezen obstakel.
- Skate een korte lijn met twee verschillende trickfamilies.
- Vind een onderdeel dat je vanaf straatniveau niet direct ziet.
- Voltooi een opdracht opnieuw met een betere uitvoering voor een extra vaardigheidsbeloning.

Er is nog geen hoofdverhaal vastgesteld. Losse opdrachten vormen de basis; NPC's kunnen later voor een lichte verhaallijn zorgen.

## 6. Spelmodus Park Runs

### 6.1 Runverloop

1. Kies je personage en uitrusting.
2. Kies een ontgrendeld park en hulppreset.
3. Bekijk de parkcommunity of start vrij oefenen.
4. Start een run met een korte aftelling.
5. Skate 90 seconden en bouw score op.
6. Bekijk de uitslag, verdiende beloningen en eventuele leaderboardpositie.
7. Bekijk een replay, praat na in de parkchat of probeer opnieuw.

**Voorstel:** de timer stopt de scoreopbouw op exact 90 seconden. Een lopende combo mag dan alleen nog worden geland om al opgebouwde punten vast te leggen; nieuwe tricks leveren na de timer geen extra punten op. Dit voorkomt onduidelijkheid en eindeloos verlengen. Definitief gedrag volgt na testen.

### 6.2 Scoreprincipes

**Vastgesteld:** moeilijkheid, uitvoering, variatie en combo's bepalen de score. Herhaling levert minder op. Bij een val gaan alleen de punten van de nog niet afgeronde combo verloren.

| Factor | Betekenis |
| --- | --- |
| Moeilijkheid | Technisch moeilijkere tricks hebben een hogere basiswaarde. |
| Uitvoering | Controle en een nette landing verbeteren de waardering. |
| Variatie | Verschillende tricks en families worden beloond; dezelfde trick blijven herhalen levert minder op. |
| Combo | Het verbinden van tricks verhoogt de waarde en het risico. |
| Geslaagde hoeveelheid | Meer goed uitgevoerde tricks kunnen meer punten opleveren, binnen de regels voor herhaling. |
| Val | De huidige onvoltooide combo vervalt; eerder vastgelegde score blijft. |

Exacte punten, vermenigvuldigers, herhalingsstraffen en voorwaarden voor het afronden van een combo zijn nog niet vastgesteld. Deze waarden komen in versieerbare scoreregels, zodat scores na grote balanswijzigingen eerlijk vergelijkbaar blijven.

### 6.3 Ranglijsten

**Voorstel:**

- Per park een ranglijst voor de beste volledige run en de beste combo.
- Aparte lijsten voor hulppresets en wezenlijk verschillende scoreregelversies.
- Filters voor week, seizoen en aller tijden.
- Optioneel later een vriendenfilter.
- Geen verplichte betaalde parkpunten in een algemene ranglijst die gratis spelers niet kunnen halen.
- Een speler heeft per ranglijst één beste resultaat; niet elke poging vult de lijst.

De precieze perioden, seizoensduur en eventuele resetregels zijn open.

### 6.4 Replays

**Vastgesteld:** vanuit een leaderboard kun je een run in de game bekijken, inclusief tricknamen en scoreopbouw. Dit mag ook als preview van een nog vergrendeld park.

**Voorstel voor de replaybediening:** afspelen/pauzeren, tijdlijn, vertraagd afspelen en een kleine selectie camerastandpunten. Spelernaam, park, hulppreset en score blijven zichtbaar.

Een replay is opgeslagen spelinformatie die opnieuw wordt weergegeven, niet standaard een grote videoupload. Ghosts om zelf tegen te rijden zijn een mogelijke latere uitbreiding, geen noodzakelijke eerste-releasefunctie.

## 7. Levels en echte locaties

| Locatie | Rol in de eerste release | Toegang |
| --- | --- | --- |
| Museumplein, Amsterdam | Echt nagebouwd park voor oefenen en runs | Mogelijk thuispark; anders vrij te spelen. |
| Forum, Barcelona | Echt nagebouwd park voor oefenen en runs | Mogelijk thuispark; anders vrij te spelen. |
| Pier 62, New York | Echt nagebouwd park voor oefenen en runs | Mogelijk thuispark; anders vrij te spelen. |
| Amsterdam centrum | Discoverywereld met spots, NPC's en opdrachten | Na de introductie beschikbaar. |

### 7.0 Skatepark Museumplein

**Vastgesteld:** het bedoelde park is het betonnen skatepark op het Museumplein, naast de spiegelvijver en het basketbalveld, met het Rijksmuseum als achtergrond. Het totale oppervlak is ongeveer 875 m² (schatting van de gebruiker; nog te meten).

Op basis van de referentiefoto's bestaat het park uit:

- een streetgedeelte met zwarte ledges, rails met kenmerkende boogvormige steunen, een trap van drie treden met leuningen, banks, een funbox/pyramide en manual pads;
- een bowl met hips, rondingen en coping;
- een bakstenen rand met zittreden langs de buitenkant.

De referentiefoto's staan in `references/museumplein/`. Exacte maten, hoogtes en radiussen moeten nog worden vastgelegd.

**Voorstel voor de bronnen:** de PDOK-luchtfoto voor de plattegrond op schaal, bouwtekeningen via de gemeente Amsterdam (of via een Woo-verzoek), eigen metingen ter plekke en een fotoscan als referentie voor de bowl. Bij het opvragen van de tekeningen kan meteen toestemming voor gebruik in de game worden gevraagd.

Omdat het park in Nederland ligt en goed bereikbaar is, is het **voorstel** om het als eerste volledige park te bouwen (zie 13.2).

### 7.1 Exacte nabouw als ontwerpeis

De gebruiker wil geen los geïnspireerde locaties: obstakels, afstanden, verhoudingen, rijlijnen, omgeving, graffiti en aankleding moeten overeenkomen met de gekozen echte locatie.

**Voorstel voor de werkwijze per locatie:**

1. Leg de exacte locatie en een referentiedatum vast; parken en graffiti veranderen.
2. Verzamel voldoende overzichtsbeelden, detailbeelden, afmetingen en informatie over gebruiksrechten.
3. Maak eerst een model met eenvoudige vormen op de juiste schaal.
4. Controleer afstanden, hoogtes en lijnen tegen de referenties.
5. Werk materialen, graffiti, aankleding en omgeving uit.
6. Optimaliseer de weergave voor mobiel zonder de afgesproken indeling stilzwijgend te veranderen.

Voor Forum moet het exact bedoelde park/gebied worden bevestigd met een kaartpin of herkenbare referentie. Voor elke locatie moet worden afgebakend hoeveel van de omliggende wijk daadwerkelijk bespeelbaar is. Een exacte visuele nabouw betekent niet automatisch dat ieder gebouw van binnen toegankelijk wordt.

### 7.2 Uitdagingen per park

Iedere locatie behoudt haar echte indeling. De game legt daar verschillende doelen overheen, zoals een technische lijn, trickvariatie of een persoonlijk record. Nieuwe doelen hoeven geen fictieve obstakels aan een echt park toe te voegen.

Extra betaalde parken zijn een mogelijke uitbreiding na de basisrelease. Ze worden gekoppeld aan een bestaande stadscommunity.

## 8. Personage, uitrusting en economie

### 8.1 Eigen skater

**Vastgesteld:** eigen personage met instelbaar gezicht, haar en lichaamstype. Outfits en uitrusting speel je later verder vrij. Vóór het starten van een spelmodus zie je de skaterselectie/loadout.

**Voorstel:** één actief personage bij de start, met opgeslagen outfits. Extra personages of meerdere slots kunnen later volgen. Een snelle start gebruikt de laatst gekozen uitrusting, zodat je niet bij iedere herstart opnieuw door alle menu's hoeft.

### 8.2 XP en coins hebben verschillende functies

| Middel | Verdienen | Gebruiken |
| --- | --- | --- |
| XP | Actief spelen, ontdekken, opdrachten en park runs | Niveau, voortgang en toegang tot uitdagingen/parken. |
| Coins | Opdrachten, ontdekking en beloningen uit runs | Skates, onderdelen en kleding in de verdiende shop. |
| Echt geld | Niet van toepassing | Duidelijk geprijsde cosmetische items en later eventueel parkpakketten. |

Coins worden niet verkocht. Er is geen tweede premiumvaluta afgesproken.

### 8.3 Parken ontgrendelen

**Vastgesteld:** een combinatie van speeltijd/voortgang en vaardigheid.

**Voorstel:** elk basispark vraagt een haalbare voortgangsmijlpaal plus één vaardigheidsopdracht. Vooruitgang komt uit actief spelen, niet uit de app laten openstaan. De tutorial leidt naar de vaardigheden die voor een volgende ontgrendeling nodig zijn.

Het exacte aantal uren, het vereiste niveau en de challenges worden pas na speeltests bepaald. Coins blijven beschikbaar voor uitrusting; toegang tot een basispark kost geen coins.

### 8.4 Uitgangspunten voor aankopen

- Alle drie basissteden en hun communities zijn zonder betaling bereikbaar.
- Betaalde cosmetica geven geen scorebonus.
- Betaalde extra parken krijgen eigen scorelijsten en delen een bestaande stadscommunity.
- Geen betaling nodig om met de gratis vrijspeelbare stadscommunity mee te praten.
- **Voorstel:** toon bij een aankoop direct het item, de prijs en wat de speler krijgt; geen lootboxes of betaalde gokmechaniek.

Exacte verkoopprijzen, catalogus, eventuele invloed van verdiende skateonderdelen op rijeigenschappen en het aankoopkanaal zijn open. Voor eerlijke competitie is het voorstel om bij de eerste release uitrusting geen prestatievoordeel te laten geven.

## 9. Thuispark en parkcommunity

### 9.1 Startkeuze

Een speler kiest een thuisregio. De game stelt een passend beschikbaar thuispark voor, maar de speler kiest zelf. Met drie startparken is er niet voor ieder land een eigen locatie.

Het gekozen thuispark is direct beschikbaar. De andere twee ontgrendel je met voortgang en vaardigheid. De eisen moeten zo worden afgestemd dat de startkeuze geen structureel score- of beloningsvoordeel oplevert.

### 9.2 Een nieuw park opent een nieuwe community

Een ontgrendeld park geeft toegang tot skaten én meepraten. De community bestaat uit spelers die dat als thuispark kozen en bezoekers die het hebben vrijgespeeld. Dat zijn niet uitsluitend mensen die daadwerkelijk in dat land wonen.

**Voorstel:** een bescheiden label `Local` of `Bezoeker` op basis van thuisparkkeuze, niet op basis van een bewezen woonadres. Wisselen van thuispark en de gevolgen daarvan zijn nog uit te werken.

### 9.3 Preview vóór ontgrendeling

**Vastgesteld:** de locatie bekijken en runs van anderen bekijken mag vóór ontgrendeling.

**Voorstel voor het previewscherm:** parkbeelden, locatie, beschikbare challenges, topscores, replays en duidelijke ontgrendelvoorwaarden. Je kunt nog geen eigen run starten of berichten plaatsen. Of vergrendelde parkchat wel leesbaar is, staat nog niet vast.

### 9.4 Tekstchat

- Openbare chat in de parkhub, logisch vóór en na een run.
- Tijdens een run klapt chat dicht; geen toetsenbord over de trickbediening.
- Berichten zijn gekoppeld aan een spelersprofiel.
- Blokkeren en rapporteren zijn vanaf het begin beschikbaar.
- Privéberichten behoren niet tot de eerste scope.
- Vrienden toevoegen is nog een open productkeuze.
- Geen voicechat in de afgesproken scope.

**Voorstel voor uitvoering:** berichtlimieten tegen spam, een afhandelroute voor meldingen en duidelijke regels voor omgang. Taalkeuze en leeftijdsbeleid moeten vóór publieke chat worden vastgesteld.

Discovery krijgt NPC-dialogen, geen openbare livewereldchat. Vanuit pauze kan eventueel een link naar de eigen parkcommunity komen; dat is nog een voorstel.

## 10. Schermen en navigatie

### 10.1 Eerste keer spelen

`Start → profiel/account → skater maken → thuispark kiezen → tutorial → hoofdmenu`

Na de tutorial kan de speler zowel Discovery als Park Runs kiezen. De tutorial gebruikt het gekozen thuispark. Hij leert bewegen, springen, een eerste grind, netjes landen en een eenvoudige combo.

Accountmoment, gastmodus en manier van aanmelden zijn nog open. De speler hoeft niet opnieuw een personage te maken als hij later een account koppelt; dit is een voorgesteld uitgangspunt.

### 10.2 Dagelijkse navigatie

`Hoofdmenu → skater/loadout bevestigen → Discovery of Park Runs`

`Park Runs → parkselectie → parkhub → oefenen/run → uitslag → replay/chat/opnieuw`

`Discovery → Amsterdam → ontdekken/opdracht → beloning → verder rijden of terug naar menu`

### 10.3 Schermenoverzicht

| Scherm | Doel en belangrijkste inhoud |
| --- | --- |
| Start/laden | Game starten, bestanden controleren, laadvoortgang tonen. |
| Profiel/account | Aanmelden of gekozen startoptie, schermnaam en profiel. |
| Personage maken | Gezicht, haar, lichaamstype, basisuitrusting en preview. |
| Thuispark kiezen | Voorstel op basis van gekozen regio; alle drie opties begrijpelijk vergelijken. |
| Tutorial | Besturing stap voor stap in het thuispark. |
| Hoofdmenu | Duidelijke toegang tot Discovery, Park Runs, skater, shop en voortgang. |
| Skater/loadout | Actieve skater bekijken, kleding en skates kiezen, modus starten. |
| Parkselectie | Drie echte parken; thuispark, ontgrendeld of vergrendeld duidelijk zichtbaar. |
| Parkpreview | Beelden, replays, topscores en ontgrendelvoorwaarden. |
| Parkhub | Oefenen, 90-secondenrun, challenges, leaderboard en tekstchat. |
| Vrij oefenen | Onbeperkt oefenen zonder runklok; snel opnieuw positioneren. |
| Run-HUD | Timer, vastgelegde score, actuele combo, tricknaam en twee touchzones. |
| Runuitslag | Scoreopbouw, persoonlijk record, rang, XP/coins en vervolgstappen. |
| Leaderboard | Beste runs/combo's met relevante filters en replayknop. |
| Replayviewer | Opgeslagen run, afspeelbediening, tricknamen en score. |
| Discovery-HUD | Besturing, compacte opdrachtinformatie en relevante interactieprompt. |
| Discoverykaart | Ontdekte spots, actieve doelen en herkenbare oriëntatiepunten. |
| NPC-gesprek | Reactie, dialoogkeuze en eventueel opdracht/beloning. |
| Opdrachtenoverzicht | Actieve en afgeronde opdrachten, voortgang en beloningen. |
| Inventaris/shop | Verdiende items, coin-aanbod en duidelijk afgescheiden directe aankopen. |
| Voortgang | XP-niveau, parkontgrendelingen en persoonlijke mijlpalen. |
| Parkchat/profiel | Berichten, profiel bekijken, blokkeren en rapporteren. |
| Instellingen/pauze | Besturing, gevoeligheid, hulp, geluid, graphics en toegankelijkheid. |

### 10.4 HUD en telefoonformaat

- Links een grote witte joystick; rechts één transparante trickpad.
- Skater, aanloop en eerstvolgende obstakel blijven vrij van grote menu's.
- In Park Runs staat de timer bovenin en is de combo duidelijk van vastgelegde score te onderscheiden.
- In Discovery vervangt compacte opdrachtinformatie de runklok.
- **Voorstel:** positie, grootte en gevoeligheid van touchzones zijn instelbaar.
- De conceptvisuals zijn 16:9. De werkelijke app moet ook bredere telefoons, uitsparingen en veilige schermmarges ondersteunen.

## 11. Technische structuur — voorstel, geen vastgelegde implementatie

### 11.1 Mobiele game

Unreal Engine is besproken als kandidaat voor realistische 3D. De definitieve keuze en inzet van MetaHuman moeten worden gevalideerd met een prototype op Android én iOS. Een gedetailleerd desktoppersonage of een gegenereerde conceptafbeelding is geen bewijs van haalbare mobiele prestaties.

**Voorgestelde onderdelen:**

- Besturing en interpretatie van gebaren.
- Skaterbeweging, animaties, grindcontact en landingen.
- Scoreregels en comboherkenning.
- Discoverywereld, opdrachten en reagerende NPC's.
- Parkruns, timer en replayopname/-weergave.
- Inventaris, personage en voortgang.
- Schermen, chatinterface en online synchronisatie.

De telefoon tekent de wereld en voert het lokale spel uit. Er is geen cloudstreaming van graphics nodig.

### 11.2 Online diensten

Voor accounts, scores, replays, voortgang, coins, aankopen en chat is een backend nodig. Azure en Epic Online Services zijn besproken als mogelijke onderdelen; de combinatie is nog niet gekozen.

Geen dedicated server die live skaters in een gedeelde wereld simuleert. Wel online verbindingen voor chat en diensten. Tekstchat is een sociale onlinefunctie, geen gedeelde simulatie.

**Voorstel voor scheiding:**

| Onderdeel | Verantwoordelijkheid |
| --- | --- |
| Mobiele client | Spelen, tekenen, besturing, lokale opname en interface. |
| Account/progressiedienst | Profiel, XP, coins, ontgrendelingen en inventaris. |
| Scoredienst | Runs ontvangen, controleren, ranglijsten bijwerken. |
| Replayopslag | Opgeslagen rungegevens beschikbaar maken. |
| Chatdienst | Parkkanalen, berichten en blokkeer-/rapportageacties. |
| Aankoopverificatie | Betaalde rechten controleren en herstellen. |
| Contentdistributie | Gamebestanden, parken en updates leveren via het gekozen kanaal. |

### 11.3 Betrouwbare scores en economie

De backend moet niet blind vertrouwen op een getal dat een telefoon opstuurt. **Voorstel:** een run bevat scoreversie, parkversie, hulppreset en voldoende gebeurtenissen om onmogelijke resultaten te signaleren. Een replay alleen bewijst nog niet dat een score eerlijk is.

Coins, betaalde rechten en ontgrendelingen worden gecontroleerd opgeslagen. Het precieze validatieniveau is open en hangt af van hoeveel competitieve betrouwbaarheid we willen bieden.

### 11.4 Offline gedrag

**Voorstel:** geïnstalleerde locaties blijven bruikbaar voor oefenen en lokale discovery. Chat en actuele leaderboards vragen internet. Het beleid voor offline verdiende coins, voortgang en competitieve scores moet apart worden ontworpen; offline scores worden niet automatisch als betrouwbaar gepubliceerd.

## 12. Visuele kwaliteit en prestaties

Het doel is een realistische uitstraling met sterke animaties, correcte inline-skates, overtuigende materialen en herkenbare locaties. Het bewegingsgevoel heeft voorrang boven details die tijdens het spelen nauwelijks zichtbaar zijn.

**Voorstellen voor de technische aanpak:** schaalbare graphics, meerdere detailniveaus, geoptimaliseerde textures en alleen de relevante omgeving tegelijk laden. Deze technieken mogen niet ongemerkt de afgesproken exacte parkindeling vervangen.

De minimale Android- en iPhone-modellen, opslagruimte, gewenste framerate en grafische presets zijn nog open. Een claim van stabiele 60 fps kan pas volgen na metingen op echte doeltoestellen.

## 13. Release en bouwvolgorde

### 13.1 Vastgestelde eerste releasescope

- Android én iOS tegelijk.
- Discovery in Amsterdam centrum met reagerende NPC's, aansluitend op het Museumplein.
- Park Runs in Museumplein (Amsterdam), Forum (Barcelona) en Pier 62 (New York).
- Eigen skater en loadoutselectie vóór de modi.
- Tutorial, oefenen en runs van 90 seconden.
- Scoring, leaderboards en replays.
- XP, verdiende coins, uitrusting en ontgrendelbare basisparken.
- Thuispark, parkpreviews en openbare parkchat met blokkeren/rapporteren.

Een winkel met verdiende items hoort bij de basis. Of betaalde cosmetica al op dag één beschikbaar zijn en wanneer betaalde parkpakketten komen, is nog open.

### 13.2 Interne bouwstappen — geen verkleining van de releasescope

1. **Besturingsprototype:** één rail, skater en enkele tricks op Android én iOS.
2. **Speelbare kern:** springen, grindwissels, vallen, landingen, scoring en replay.
3. **Eén volledig park:** referenties, schaal, aankleding, tutorial en 90-secondenrun. **Voorstel:** Museumplein als eerste park, omdat het in Nederland ligt en ter plekke te meten en te scannen is.
4. **Progressie en online laag:** profiel, inventory, XP/coins, scoreverwerking en chat.
5. **Overige parken en Discovery:** Forum, Pier 62 en Amsterdam met NPC's/opdrachten.
6. **Gezamenlijke releasevoorbereiding:** prestaties, toegankelijkheid, aankopen indien gekozen, chatbeheer en controles op beide platforms.

De gebruiker heeft gekozen voor beide modi bij de eerste release. Deze bouwvolgorde betekent dus niet dat Discovery wordt uitgesteld tot na publicatie.

## 14. Kosten en distributie

De gebruiker en assistent werken het project zelf uit. Ontwikkelaarsalarissen en ingehuurde ontwikkel-/animatiewerkzaamheden worden niet als gewenste begrotingspost opgenomen.

De eerdere bedragen voor een downloadbare pc-game zijn geen bevestigde begroting voor dit mobiele concept. Er is nu geen live gameserver nodig, maar kosten kunnen ontstaan voor backend, chat, opslag, replays, contentverkeer, optionele tools en distributie/aankopen.

Epic Games Store en Epic Online Services zijn eerder onderzocht, maar zijn verschillende keuzes: een distributiekanaal tegenover online diensten. Definitieve distributie naar Android en iOS, betaalafhandeling en toepasselijke kosten zijn nog niet vastgesteld.

Er wordt niets uitgerold in de bestaande Prakkie-Azure-resources op basis van dit document.

## 15. Open punten vóór definitieve productieplanning

1. Definitieve gamenaam, visuele identiteit en talen.
2. Exacte kaartgrens van Amsterdam voor Discovery en de aansluiting op het Museumplein.
3. Kaartpin/referenties voor het bedoelde Forum-park. (Het Museumplein-park is in versie 1.1 vastgesteld.)
4. Referentiedatum, afmetingen en bronmateriaal per locatie, inclusief graffiti en aankleding. Voor Museumplein: opmeten, bouwtekeningen opvragen en een fotoscan van de bowl maken.
5. Controle van benodigde rechten voor exact gereproduceerde beelden, kunst, namen en andere content, waaronder toestemming van de gemeente Amsterdam en de ontwerper van het Museumplein-park.
6. Definitieve engine, doeltoestellen, prestatiebudget en downloadomvang.
7. Geteste trickgebaren en complete bediening van sprongen, grinds, spins, fakie en switch.
8. Puntenformule, comboafronding, hulppresets en leaderboardperioden.
9. XP-tempo, coinbeloningen, parkvoorwaarden en prijzen van shopitems.
10. Detailniveau van NPC-reacties en eventuele lichte verhaallijn.
11. Thuispark wisselen, vriendenfunctie en leesbaarheid van vergrendelde parkchat.
12. Accountflow, leeftijdsbeleid, chatmoderatie en offline synchronisatie.
13. Distributie en aankoopkanalen voor beide mobiele platforms.
14. Of directe betaalde cosmetica al in de eerste release verschijnen.

Open punten veranderen de vastgestelde richting niet. Ze voorkomen dat nog onbesproken details als definitief worden behandeld.

## 16. Eerdere visuals

### Oorspronkelijke sfeer- en HUD-studie

![Sfeerbeeld van een mobiele inline-skategame in een park](assets/gameplay-concept.png)

AI-gegenereerde sfeerreferentie. De aparte jumpknop en switchknop in dit beeld zijn niet de gekozen eindbediening. Dit is ook geen nabouw van een van de drie definitieve parken.

### Gekozen richting voor de besturing

![Vier stappen voor springen en tricks kiezen met één rechterduim](assets/touch-controls-concept.png)

Indrukken → vasthouden en slepen → loslaten → tijdens de grind opnieuw slepen. AI-gegenereerde uitleg van het bedieningsidee; skatehoudingen en contactpunten in de afbeelding zijn geen technische animatiereferentie. Speelgevoel en herkenning van gebaren moeten nog worden getest.

## 17. Definitie van de huidige status

Het concept is vastgelegd. Er is nog geen speelbare game, betrouwbare kostenraming voor deze mobiele scope, bevestigde locatie-opname, publieke chatdienst of definitieve planning. De eerstvolgende bouwstap is een kleine, toetsbare demonstratie van de gekozen besturing op beide mobiele platforms, binnen de scope van de eerste release: Discovery in Amsterdam en Park Runs in Museumplein, Forum en Pier 62.
