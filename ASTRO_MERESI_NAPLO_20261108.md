# ASTRO — mért eredmények és referencia-pontosság

Dátum: 2026-11-08. Helyi fizikai mérések: RTX 4060 Ti / CUDA és két RX 470 / Vulkan.
Az alábbi adatok a teljes kutatási munkakészlet mérései; nem a most csomagolt szintetikus bench eredményei.
A számok az elmentett futási és ellenőrzési jegyzőkönyvekből származnak.

## Feldolgozott munkakészlet egy teljes futásban

| Terület | Teljes feldolgozott mennyiség |
| --- | --- |
| BIO / SBML | 5 külön modell; modellenként mind az 51 időpont, mindkét faj, 128 ismételt példány |
| SIGNAL / MIT-BIH | Mind a 48 rekord teljes első elvezetése; 31 200 000 minta |
| CHEM / NIST LJ | Mind a 4 konfiguráció × 3 séma = 12 kombináció |
| SPACE | 1 adaptált Kepler-pálya, 128 ismételt példány |
| PDEBench / Burgers | 10 000 külön trajektória × 201 időpont × 1024 cella = 2 058 240 000 érték |

Egy munkakészlet 64 belső darabban, 69 gráfkiértékeléssel készült el. Ez nem 64 külön teljes kutatási munka.
Az első kampány ugyanazt a munkakészletet 6-szor, az RTX-ismétlés további 2-szer dolgozta fel.
Összesen 8 teljes feldolgozás, 1 különböző munkakészlet, 7 összehasonlítási ismétlés; 552 belső gráfkiértékelés.
Az első darab több tudományterületet tartalmazott ugyanazon GPU közös sessionjében; a további darabok PDE-munkák voltak.
A lefedettség nem a teljes SBML-tesztcsomag vagy a teljes Basilisk-munkafolyamat. A referenciahibás SPC/E nincs az elfogadott esetek között.

## Első teljes kampány: 6 fizikai munkamenet

Minden idő másodperc. CPU: a teljes folyamatfa CPU-ideje. GPU: eseményekből összesített idő.

| GPU | Adatút | Teljes E2E | CPU-idő | Tudományos GPU-idő | Tömörítő GPU-idő |
| --- | --- | ---: | ---: | ---: | ---: |
| RTX 4060 Ti | raw | 376.669036 | 104.632438 | 93.191197 | 0.000000 |
| RTX 4060 Ti | qgc1 | 787.385656 | 264.157173 | 94.110800 | 1.489654 |
| RX 470 ×8 | raw | 394.860040 | 148.740429 | 34.864394 | 0.000000 |
| RX 470 ×8 | qgc1 | 250.895690 | 291.114153 | 35.020317 | 2.217084 |
| RX 470 ×1 | raw | 250.562766 | 160.009426 | 34.252381 | 0.000000 |
| RX 470 ×1 | qgc1 | 248.467996 | 288.192059 | 34.257332 | 2.110674 |

Teljes kampány: 3149,743729 s falióra-idő; 1514,892634 s folyamatfa-CPU-idő.
Ebben az első tömörített referencia elkészítése és a megszakított CPU-előkészítés költsége is szerepel.
A CPU-előkészítés folytatása nem járt GPU-újrafuttatással.
Backend-puffercsúcs: RTX 1 300 558 192 bájt, Radeon 1 325 724 144 bájt; mind 2 GiB alatt.
Ez nem a driver teljes VRAM-foglalása. A tömörített út teljes audittal mindhárom kártyán több CPU-időt igényelt.

## RTX: teljes újrafuttatás

| Adatút | Teljes E2E | CPU-idő | Tudományos GPU-idő | Tömörítő GPU-idő |
| --- | ---: | ---: | ---: | ---: |
| raw | 170.713195 | 93.219888 | 91.431878 | 0.000000 |
| qgc1 | 270.267095 | 255.255319 | 94.130787 | 1.476443 |

Két teljes munkamenet együtt: 442,612778 s falióra-idő; 350,033850 s folyamatfa-CPU-idő.
Azonos korábbi RTX-kimenettel egyezett mind a 128 nyers és mind a 128 tömörített eredményfájl.

| RTX hostszakasz | Előző mérés (s) | Új mérés (s) |
| --- | ---: | ---: |
| Nyers eredmény mentése | 255,100641 | 17,861920 |
| Tömörített eredmény mentése | 21,513768 | 4,408518 |
| Tömörített referencia olvasása, ellenőrzése és lezárása | 470,862260 | 105,9175 |
| Független teljes kibontásos bitellenőrzés | 195,814723 | 145,3641 |

A host várakozási ideje csökkent. A TRIM önálló okozati hatását ez a mérési elrendezés nem választja szét a cache-, írási és egyéb rendszerállapottól.
A szakaszok átfedhetnek, ezért nem összeadhatók. A mentés operációsrendszer-pufferelt; az E2E nem garantált fsync-ig mért tartós lemezre írás.
A referencia-előkészítés 128 cache-találatot és 0 hiányt rögzített, 1,294022 s falióra- és 1,244084 s CPU-idővel.

## Adatátvitel és tömörítés

A GPU→host mennyiség tartalmazza a tömörítési metaadatot és a nyers fallbacket is.

| Terület | Eredeti bájt | Tényleges GPU→host bájt QGC1-gyel | Eredeti / átvitt |
| --- | ---: | ---: | ---: |
| BIO | 522,240 | 503,528 | 1.037162 |
| SIGNAL | 260,000,000 | 23,466,920 | 11.079426 |
| SPACE | 1,198,080 | 1,198,144 | 0.999947 |
| CHEM | 288 | 1,056 | 0.272727 |
| PDE | 16,465,920,000 | 15,160,452,192 | 1.086110 |

Összesen: 16 727 640 608 → 15 185 621 840 bájt; csökkenés **9,218388%**.
Egy munkamenet 13 015 tudományos dispatch; QGC1 esetén további 12 189 tömörítő dispatch.
A teljes 8 munkamenetben 104 120 tudományos és 48 756 tömörítő dispatch szerepel.
Internetes átvitelt és energiát ezekben a futásokban nem mértek.

## Pontosság a referenciákhoz képest

Az alábbiak a teljes kimenet ellenőrzési eredményei. A táblázat a három kártyán mért legnagyobb eltérést mutatja.

| Munka | Referencia / kapu | Mért eltérés, találati arány | Eredmény |
| --- | --- | --- | --- |
| SBML | Publikált, esetenkénti abszolút + relatív tűrés | Legnagyobb abszolút hiba 6,2198279513×10⁻¹¹; a megengedett tűrés legfeljebb 6,1336633375×10⁻⁷ része | 5/5 modell PASS; nem ZERO BIT állítás |
| NIST Lennard–Jones | A publikált számok megadott pontosságából származtatott tűrés | Legnagyobb abszolút eltérés 0,049650713200; tűréskihasználás legfeljebb 0,993014240855 | 12/12 kombináció PASS; nem ZERO BIT állítás |
| MIT-BIH EKG | Ütésannotációk, ±150 ms illesztés | TP 108 461; FP 672; FN 1007; érzékenység 99,0800965%; pozitív prediktív érték 99,3842376% | SCORED; nem klinikai PASS |
| Kepler | Független, 60 tizedesjegyes analitikus megoldás | Pozícióhiba ≤0,030468298706 m; sebességhiba ≤0,000032957061143 m/s; relatív energiadrift ≤5,0835240153×10⁻¹¹ | Mérnöki kapu PASS: 0,1 m / 0,0001 m/s / 10⁻⁸; nem Basilisk-tanúsítás |
| PDEBench Burgers | Teljes letöltött referenciatömb, előre megadott mérnöki tűrés | Legnagyobb relatív L2-hiba 0,00107073951812; legnagyobb abszolút hiba 0,0297906912121 | Mind a 10 000 trajektória PASS; határok 0,01 és 0,05 |
| QGC1 veszteségmentesség | Független dekóder, ugyanazon kártya friss nyers eredménye | Mind a 16 727 640 608 eredeti bájt ellenőrizve minden tömörített teljes futásnál; 0 eltérő bit | ZERO BIT |

Az EKG belső implementáció-egyezése ZERO BIT; ez külön állítás a fenti annotációs pontosságtól.
RTX és Radeon között 128 nyers kimenetből 123 volt bitazonos, 5 eltért. Általános kártyák közötti ZERO BIT nincs igazolva.
Az online tömörített ellenőrzés és a külön teljes dekóderes audit együtt szerepel a QGC1 E2E- és CPU-költségében.

Mérési források a helyben megőrzött jegyzőkönyvekben: `full-run-20261108T174516Z`,
`FULL_AUDITED_RESULT.json`, `rtx-rerun-20261108T184513Z/results/SUMMARY.json`,
`HOST_COMPARISON.json`, munkánkénti `VERIFICATION.json` és natív eseménynyomok.
A közzétett napló összesítés: a nyers kutatási fájlokat és hash-jegyzékeket nem tartalmazza.
Független külső újramérés nem része ennek a jelentésnek.
