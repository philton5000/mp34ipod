---
name: download-playlist-mp3
description: "Télécharger une playlist Spotify en MP3 avec numérotation, anti-doublons et nettoyage >20Mo. Utilise yt-dlp et le script download_anti_duplicate.py."
---

# Download Playlist MP3

Usage : `python3 ~/Music/Latin_Playlist/download_anti_duplicate.py`

## Prérequis
- `yt-dlp` (installé via pip ou système)
- `ffmpeg` (déjà présent dans le système)
- Script `download_anti_duplicate.py` dans `~/Music/Latin_Playlist/`

## Fonctionnement
- Lit la liste fournie par l'utilisateur (fichier texte avec numéros, titres, artistes)
- Télécharge chaque morceau via `yt-dlp` (`ytsearch`)
- Nom de fichier formaté : `{num:03d} - {titre} - {artiste}.mp3`
- Nettoyage automatique : supprime tout MP3 >20 Mo
- Anti-doublons : skip si le titre/artiste correspond déjà

## Procédure (étapes dans l'ordre)
1. Vérifier que `yt-dlp`, `ffmpeg` et `PATH` sont configurés.
2. Fournir la liste complète (fichier texte : lignes numérotées, titre, artiste).
3. Lancer le script : `python3 ~/Music/Latin_Playlist/download_anti_duplicate.py`
4. Contrôler le nombre de téléchargements avec `MAX_DL` (défaut 3, ex. `export MAX_DL=400`).
5. Vérifier le résultat dans `~/Music/Latin_Playlist/` (format `{num:03d} - Titre - Artiste.mp3`).
6. Appliquer le nettoyage `>20Mo` automatiquement (le script le fait au lancement et après chaque succès).

## Pitfalls
- Le format du nom doit conserver les caractères lisibles (parenthèses, accents, tirets) et ne pas remplacer tout par des underscores. Utiliser `clean_for_filename` qui ne remplace que `\\/:*?"<>|`.
- Le numéro doit être extrait depuis le fichier texte fourni par l'utilisateur (vérifier `lines[i-1]` et `lines[i-2]` car il peut y avoir une ligne vide entre le numéro et le titre).
- Le script (`download_anti_duplicate.py`) doit être commité et poussé automatiquement après chaque modification (`watch_push.py` surveille le fichier et applique `git commit + git push`).
- Ne pas supprimer le module `savify` si on veut l'utiliser ; il est supprimé définitivement dans cet environnement (`~/savify` + `pip uninstall`).

## Limites
- `ytsearch` retourne des résultats YouTube approximatifs (pas toujours la version Spotify exacte)
- Projet `savify` (`~/savify`, module pip) supprimé définitivement ; le script personnalisé reste la méthode recommandée
- Pour des téléchargements exacts avec métadonnées Spotify, utiliser `savify` (nécessite `SPOTIPY_CLIENT_ID` + `SPOTIPY_CLIENT_SECRET` et un compte Spotify Premium) — non installé actuellement

## Variables d'environnement
- `MAX_DL` : nombre max de téléchargements par session (défaut 3)
- `PATH` : doit inclure `/Users/admin/Library/Python/3.9/bin/`
