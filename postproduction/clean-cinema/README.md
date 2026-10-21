# Aethers Club — Clean Natural Cinema, revisione 3

La direzione visiva segue la seconda parte del **primo video grezzo**, dalla panchina al cancello: felpa grigia, cambio nel capo bianco e luce naturale sulle pareti. Il finishing conserva il rosa della location, i bianchi del capo, la grafica blu e la pelle.

Il nuovo montaggio dura **26,000 secondi, 624 frame a 24 fps** e usa sei clip, con cinque raccordi netti. Il cambio alla panchina rimane continuo. Le due accelerazioni della corsa sono moderate; i gesti del cambio e la camminata restano quasi a velocità naturale. La nuova configurazione non contiene whip sintetici, flash, punch zoom, titoli, badge o grafiche social. La grafica fisicamente stampata sul capo appartiene al girato.

## File del progetto

- `Aethers_Club_Clean_Cinema.mp4`: nuova esportazione H.264/AAC, nativa 848×480, con avvio rapido.
- `NLE_GUIDE.md`: indicazioni per DaVinci Resolve, Premiere Pro e CapCut.
- `post-production.json`: configurazione completa e revisionata del renderer.
- `cutlist.csv`: In/Out sorgente e timeline, frame, timecode, velocità e azione.
- `Aethers_Clean_Natural_Rec709.cube`: LUT creativa 33³, per materiale già SDR Rec.709.
- `clean_grade.py` e `render_clean.py`: implementazione riproducibile da sorgente.

La LUT contiene soltanto il look cromatico comune. Bilanciamenti delle singole riprese, stabilizzazione, grana e nitidezza sono passaggi separati. I parametri dei tre editor sono documentati come punti di partenza: non è stato modificato alcun loro progetto nativo.

## Scaletta dei tagli

Timecode timeline `HH:MM:SS:FF`, 24 fps esatti. Gli Out sono esclusivi. I tempi sorgente sono secondi reali del file originale, circa 23,976 fps.

| Clip | Timeline In → Out | Sorgente In → Out, secondi | Velocità | Azione |
|---|---|---|---:|---|
| C01 | 00:00:00:00 → 00:00:03:17 | 0,000000 → 4,921667 | 1,327191× | Presentazione, partenza del protagonista e inseguitore: prima ripresa continua. |
| C02 | 00:00:03:17 → 00:00:04:09 | 4,921667 → 5,755000 | 1,249999× | Secondo angolo, corsa del protagonista. |
| C03 | 00:00:04:09 → 00:00:05:06 | 7,256667 → 8,341667 | 1,240000× | Secondo angolo, corsa dell’inseguitore. |
| C04 | 00:00:05:06 → 00:00:06:20 | 8,341667 → 9,926667 | 1,001053× | Approccio e scavalcamento del muro. |
| C05 | 00:00:06:20 → 00:00:19:11 | 9,926667 → 22,565000 | 1,001056× | Discesa, atterraggio e intero cambio alla panchina. |
| C06 | 00:00:19:11 → 00:00:26:00 | 23,273333 → 29,821667 | 1,001019× | Nuovo look, passaggio dell’inseguitore e camminata finale. |

Lo scarto temporale fra capo in mano e capo indossato è già presente nel girato: si raccorda direttamente al cancello. Non si ricostruisce un gesto che la camera non ha registrato. La sequenza chiude prima del passaggio dell’auto.

## Luce, movimento e texture

Bilanciamento separato delle cinque riprese originali, curva con nero ancorato a zero e shoulder morbida, calore tenue nelle luci e ombre neutre. La maglia non deve diventare crema e i neri non devono diventare grigi. Grana monocromatica fine, denoise lieve e sharpening contenuto.

Stabilizzazione 2D per ripresa, con correzione limitata a 2 pixel e 0,0015 radianti, smoothing di 4 frame e zoom fisso del 2%. Si preserva il movimento residuo naturale, senza cambiare prospettiva o costruire movimenti di camera nuovi. Il crop fisso di sicurezza non è uno zoom animato.

L’audio originale segue i nuovi tagli e le nuove velocità. Non è stata aggiunta musica e non è imposta una griglia a 120 BPM.

## Riprodurre il render

Servono Python 3 con NumPy, FFmpeg con `libvidstab` e `libx264`, e `ffprobe`. Eseguire dalla cartella che contiene questi file:

```bash
python render_clean.py \
  --source '/percorso/WhatsApp Video 2026-10-20 at 22.09.58.mp4' \
  --config post-production.json \
  --output Aethers_Club_Clean_Cinema.mp4
```

La configurazione è specifica del sorgente originale di 730 frame. I file `stabilization/`, il video intermedio e il manifest vengono generati durante l’elaborazione. Il renderer verifica durata, conteggio frame e decodifica del file esportato.

LUT e configurazione non recuperano dettagli persi nella compressione WhatsApp, aree già sovraesposte o illuminazione fisica assente dal girato. L’export rimane alla risoluzione nativa, senza attribuire a un ingrandimento nuovo dettaglio HD.
