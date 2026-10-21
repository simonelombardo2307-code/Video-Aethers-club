# Aethers Club — guida al finishing cinematografico pulito

Il riferimento visivo è la **seconda parte del primo video grezzo**, dalla panchina all’uscita in maglietta bianca: sole naturale, pelle credibile, maglia bianca leggibile, nero denso e contrasto ricco. La configurazione riguarda il nuovo montaggio pulito di **26 secondi, 624 frame a 24 fps**, con sei segmenti di montaggio. Non sono stati modificati progetti nativi di Resolve, Premiere o CapCut.

## Base colore e ordine degli interventi

1. Impostare un progetto **SDR Rec.709**, con monitoraggio di riferimento gamma 2.4. Il file originale è già Rec.709: non assegnargli un profilo Log o HDR e non introdurre trasformazioni duplicate.
2. Bilanciare separatamente le cinque riprese originali: esposizione e dominante prima del look. La prima scena è già calda; non applicare a tutte un identico aumento di temperatura. Usare pelle e capo bianco come controllo, conservando il calore reale del sole e il rosa delle pareti.
3. Applicare **Aethers_Clean_Natural_Rec709.cube**, LUT creativa 33³ per immagini Rec.709, dopo il bilanciamento. Partire da intensità **100%**, riducibile indicativamente a **70–100%** secondo l’inquadratura. Le modalità per dosarla dipendono dall’editor.
4. Controllare pelle, grafica blu e bianchi; aggiungere soltanto dopo la grana e l’eventuale nitidezza minima.

La LUT contiene curva di contrasto a S, compressione morbida delle alte luci, calore naturale con protezione dei bianchi e riduzione moderata dei verdi, circa 10–15%. Non include bilanciamento del bianco per clip, stabilizzazione, grana, sharpening o vignettatura. Non introduce ombre blu o neri sollevati. I valori manuali sottostanti sono un’alternativa alla LUT: non sommare automaticamente entrambi i trattamenti completi.

**Obiettivi sugli scopes**, da interpretare sulla scena: neri significativi circa **2–5 IRE**, con tessuto e recinzione ancora leggibili; bianco diffuso della maglia **80–90 IRE**; riflessi diurni fino a circa **95 IRE**. Non portare ogni ombra a zero e non rendere grigio il nero. Mantenere la luce solare brillante senza appiattire tutte le alte luci.

## DaVinci Resolve

- Impostare timeline e uscita Rec.709/gamma 2.4; verificare che la gestione colore non converta nuovamente il sorgente SDR prima della LUT.
- Catena consigliata: eventuale riduzione rumore lieve → bilanciamento/esposizione → LUT → correzioni selettive → grana finale. Dosare la LUT tramite il controllo di intensità disponibile, ad esempio l’uscita Key del nodo dedicato.
- Alternativa manuale iniziale: **Contrast 1,08–1,12**, **Pivot 0,40–0,45**, shoulder morbida con curve. Regolare Lift/Gamma/Gain guardando waveform e pelle; nessun valore di Lift fisso uguale per tutte le clip.
- Riduzione rumore e grana dipendono dall’edizione e dagli effetti disponibili. Non sostituire la riduzione rumore con una sfocatura generale.

## Premiere Pro

- Usare una sequenza SDR Rec.709, senza assegnazione Log o conversione HDR automatica al materiale già SDR.
- In Lumetri eseguire prima il bilanciamento per clip. Applicare poi la LUT in un passaggio creativo separato, dove disponibile, e dosarne l’intensità; controllare infine curva e selezioni cromatiche.
- Alternativa manuale iniziale sulla scala relativa Lumetri: **Contrast +8…+15**, **Highlights −15…−25**, **Blacks −3…−6**. Sono punti di partenza, non valori da copiare in Resolve. Temperatura e tinta si regolano per ripresa, senza trasformare la maglietta in crema.
- Aggiungere la grana in un passaggio finale controllabile. Non aumentare contemporaneamente sharpening, contrasto e chiarezza per simulare dettaglio.

## CapCut

- Conservare il trattamento SDR/Rec.709. Se la versione installata permette l’importazione di LUT `.cube`, usare la LUT dopo le correzioni di base e verificarne la resa sul capo bianco.
- Altrimenti ricreare manualmente gli obiettivi sugli scopes e sul riferimento. Se i controlli sono su scala **−100/+100**, un inizio prudente è contrasto **+8…+12**, alte luci **−10…−20**, ombre/neri leggermente ridotti. Questi numeri sono indicativi: con scale o controlli differenti non sono trasferibili direttamente.
- Disattivare filtri automatici, miglioramenti viso e trattamenti HDR che alterino la pelle o appiattiscano il contrasto. Verificare nella versione usata la disponibilità di curve, LUT e grana.

## Movimento e texture

La configurazione del renderer usa stabilizzazione non prospettica `libvidstab` separata per le cinque riprese: smoothing **4**, finestra di **9 frame**, correzione massima di traslazione **2 pixel** e rotazione **0,0015 radianti**, crop costante **2%**, zoom automatico disattivato. Sono parametri del renderer, non numeri equivalenti degli slider dei tre editor. In un NLE cercare lo stesso risultato: solo microjitter corretto, mantenendo movimento e tempi originali. Controllare piedi, bordi e linee delle pareti; ridurre l’intervento se compaiono deformazioni o galleggiamento.

Grana analogica molto fine, prevalentemente monocromatica: riferimento circa **0,4–0,7 livelli su 255 RMS** alla risoluzione nativa, non una percentuale universale di effetto. Denoise cromatico lieve soltanto dove serve, nitidezza contenuta. Non aggiungere vignettatura marcata, flash, whip sintetici, crop alternati, badge o scritte social. I raccordi sono tagli netti motivati dai gesti.

## Esportazione e limiti

Esportare **MP4 H.264, 848×480 progressivo, pixel quadrati, 24 fps, 26 secondi**, tag Rec.709 e audio AAC. Il renderer usa **CRF 16**; CRF non equivale direttamente ai controlli bitrate dei NLE. Nei NLE che richiedono bitrate invece di CRF, partire da H.264 High, VBR circa 8 Mb/s e massimo 12 Mb/s, audio AAC stereo 48 kHz a 192 kb/s; adattare ai controlli disponibili. Questo margine evita una compressione aggressiva e non crea dettaglio aggiuntivo. Verificare il file esportato, non soltanto il viewer.

Il finishing può uniformare luce percepita e colore e attenuare artefatti lievi. Le zone già bruciate, il dettaglio perso nella compressione WhatsApp e la luce fisica non registrata non sono recuperabili fedelmente. Un ingrandimento non produce nuovo dettaglio HD e la stabilizzazione 2D non ricrea una ripresa effettuata con un’altra camera.
