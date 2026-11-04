---
name: zones
description: Zonage : jour, nuit, services, et les surfaces.
argument-hint: "[image du plan]"
disable-model-invocation: true
---

Fais un plan de zonage. Trois aplats de couleur doux : les pièces de jour, les pièces de nuit, les services et circulations. Sous le plan, un tableau net des pièces avec leur surface, un sous-total par zone et le total, tous calculés depuis `plan.json`, et une barre de proportion jour, nuit, services. Vidéo : les zones se colorent l'une après l'autre et le total monte jusqu'à sa valeur.

Plan donné : $ARGUMENTS (s'il n'y a rien, prends l'image de plan du dossier courant).

Commence toujours comme ça :
1. Ouvre l'image du plan et lis-la vraiment : l'échelle ou les cotes, le nord, les pièces, les murs, les portes, les fenêtres.
2. Si `plan.json` existe déjà, réutilise-le. Sinon écris-le : pièces (nom, polygone en mètres, surface), murs (segments, épaisseur), ouvertures (type, position, largeur), nord, emprise. Écris aussi ce que tu n'as pas pu lire.
3. Vérifie ta lecture avant de dessiner : les surfaces calculées doivent coller à celles écrites sur le plan (écart de 5 % au plus), sinon corrige `plan.json`.

Dessine ensuite en code, avec un script Python (matplotlib, numpy, Pillow ; installe ce qui manque avec pip, et ffmpeg sert à la vidéo). Aucun générateur d'images : tout se calcule depuis `plan.json`.

Ce que tu rends, dans le dossier courant :
- `zones.png` : le dessin final, 1080 × 1920 en portrait, sans marge perdue. Le dessin doit occuper au moins 70 % de la hauteur. Trait net, niveau d'un rendu d'école d'architecture ou d'agence, jamais un graphique de tableur. Pas de titre géant : un petit cartouche discret (nom du dessin, échelle graphique, nord si le dessin est en plan).
- `zones.mp4` : 3 s, 1080 × 1920, 30 i/s, H.264, yuv420p, où le dessin se construit sous les yeux et se termine sur l'image finale tenue les 20 dernières images. La première image n'est jamais vide.

Ouvre le PNG pour le regarder, et corrige s'il y a du texte coupé ou qui se chevauche. Termine en disant en quelques lignes ce que le dessin montre, ce que tu as lu sur le plan et ce que tu as supposé parce que le plan ne le dit pas. N'invente rien sans le dire.
