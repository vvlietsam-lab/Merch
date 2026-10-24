# Xamuel Merch Lab

Mockup-studio voor de Xamuel merch-lijn. Artwork wordt op echte shirtfoto's gezet (plooien en schaduw van de stof), met plaatsing in cm en een tech pack voor de drukker.

**Live:** https://vvlietsam-lab.github.io/merch/

## Mappen
- `index.html` — de studio (één bestand, WebGL)
- `blanks2/` — lege shirtfoto's + plooi/schaduw-maps + kalibratie (`.json`)
- `art/` — drukbestanden: per element een `.svg` (vector, voor de drukker) en `.png` (preview)
- `designs.json` — de ontwerpen die de studio laadt
- `tools/` — Python-scripts waarmee de artwork en de blank-maps gemaakt zijn

## Let op
- Op GitHub Pages worden wijzigingen alleen lokaal in je browser bewaard. De versie in claude.ai slaat ontwerpen gedeeld op.
- cm-maten zijn afgeleid van een aangenomen borstbreedte van 60 cm; definitief maken met de maattabel van de drukker.
