---
name: ombres
description: Ombres d'une journée, calculées heure par heure.
argument-hint: "[image du plan]"
disable-model-invocation: true
---

Fais une étude d'ombres en plan pour Paris (48,85° N), le 21 juin, de 8 h à 20 h, heure solaire. Calcule vraiment la hauteur et l'azimut du soleil heure par heure avec les formules astronomiques et oriente-les selon le nord du plan. Hauteur des murs 2,70 m si le plan ne dit rien (dis-le). Projette l'emprise au sol : le plan en noir, l'ombre en aplat translucide, l'heure et l'angle écrits en grand. PNG : la superposition des ombres de 8 h, 12 h et 18 h. Vidéo : l'ombre tourne autour de la maison de 8 h à 20 h et l'heure défile.

Plan donné : $ARGUMENTS (s'il n'y a rien, prends l'image de plan du dossier courant).

Commence toujours comme ça :
1. Ouvre l'image du plan et lis-la vraiment : l'échelle ou les cotes, le nord, les pièces, les murs, les portes, les fenêtres.
2. Si `plan.json` existe déjà, réutilise-le. Sinon écris-le : pièces (nom, polygone en mètres, surface), murs (segments, épaisseur), ouvertures (type, position, largeur), nord, emprise. Écris aussi ce que tu n'as pas pu lire.
3. Vérifie ta lecture avant de dessiner : les surfaces calculées doivent coller à celles écrites sur le plan (écart de 5 % au plus), sinon corrige `plan.json`.

Dessine ensuite en code, avec un script Python (matplotlib, numpy, Pillow ; installe ce qui manque avec pip, et ffmpeg sert à la vidéo). Aucun générateur d'images : tout se calcule depuis `plan.json`.

Ce que tu rends, dans le dossier courant :
- `ombres.png` : le dessin final, 1080 × 1920 en portrait, sans marge perdue. Le dessin doit occuper au moins 70 % de la hauteur. Trait net, niveau d'un rendu d'école d'architecture ou d'agence, jamais un graphique de tableur. Pas de titre géant : un petit cartouche discret (nom du dessin, échelle graphique, nord si le dessin est en plan).
- `ombres.mp4` : 3 s, 1080 × 1920, 30 i/s, H.264, yuv420p, où le dessin se construit sous les yeux et se termine sur l'image finale tenue les 20 dernières images. La première image n'est jamais vide.

Ouvre le PNG pour le regarder, et corrige s'il y a du texte coupé ou qui se chevauche. Termine en disant en quelques lignes ce que le dessin montre, ce que tu as lu sur le plan et ce que tu as supposé parce que le plan ne le dit pas. N'invente rien sans le dire.
