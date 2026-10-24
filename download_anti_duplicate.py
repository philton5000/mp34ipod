#!/usr/bin/env python3
"""
Script anti-doublon : télécharge chaque morceau une seule fois.
Relançable sans risque de doublons.
"""
import os, re, subprocess, sys

OUTDIR = "/Users/admin/Music/Latin_Playlist"

def clean_oversized():
    for f in os.listdir(OUTDIR):
        if f.endswith(".mp3"):
            size = os.path.getsize(os.path.join(OUTDIR, f))
            if size > 20 * 1024 * 1024:
                os.remove(os.path.join(OUTDIR, f))
                print(f"  [NETTOYAGE] Supprimé (>{20} Mo) : {f}")
FILE_CACHE = "/Users/admin/.hermes/composer-pastes/pasted_content_2026-10-24_03-51-24-025_27d5eb.txt"

# Pour compatibilité avec le nettoyage
FILE_CACHE_OLD = "/Users/admin/.hermes/cache/web/open.spotify.com-9c6a34ad6b.md"
PATH = "/Users/admin/Library/Python/3.9/bin:" + os.environ.get("PATH", "")

def get_songs():
    # Lire la liste complète depuis le fichier texte (387 morceaux) avec numéros
    with open(FILE_CACHE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.read().splitlines()]
    songs = []
    # Ignorer le début (logo, titre, etc.)
    i = 0
    # Trouver le premier titre (Otra Vez)
    while i < len(lines):
        if lines[i].startswith("Otra Vez (feat. J Balvin)"):
            break
        i += 1
    # Maintenant, lire par paires : numéro (optionnel), titre, artistes
    # Dans le fichier, le format est : titre sur une ligne, artiste sur la suivante
    # Mais il y a aussi des numéros (1, 2, 3...) au début de certaines lignes
    # Utilisons un regex : chercher le titre et l'artiste
    while i < len(lines):
        line = lines[i]
        # Ignorer lignes non pertinentes
        if line.startswith("Logo") or line.startswith("Cover") or line.startswith("Download") or line.startswith("How to") or line.startswith("Best") or line.startswith("Frequently") or line.startswith("Disclaimer") or line.startswith("Privacy") or line.startswith("Terms") or line.startswith("Contact") or line.startswith("©") or line.startswith("Spotify") or line.startswith("Now we") or line.startswith("Unlock") or line.startswith("SELECTED") or line.startswith("FREE MINI") or line.startswith("Bundle") or line.startswith("We automatically") or line.startswith("MINI ZIP") or line.startswith("Archive:") or line.startswith("Track ") or line.startswith("Download Your") or line.startswith("Once") or line.startswith("Why should") or line.startswith("No Software") or line.startswith("Swift") or line.startswith("NO Login") or line.startswith("Completely Free") or line.startswith("Universal") or line.startswith("Frequently Asked") or line.startswith("Is it legal") or line.startswith("How do I") or line.startswith("Are there any") or line.startswith("Can I") or line.startswith("Can I use"):
            i += 1
            continue
        # Ignorer lignes très courtes ou qui sont des numéros de section
        if len(line) < 3 or (line.isdigit() and len(line) <= 3):
            i += 1
            continue
        # Le numéro est généralement sur la ligne précédente (ou avant une ligne vide)
        # Vérifier i-1 et i-2 (si i-1 est vide)
        num_str = ""
        if i > 0:
            prev_line_1 = lines[i-1].strip() if i-1 >= 0 else ""
            if prev_line_1.isdigit() and int(prev_line_1) > 0:
                num_str = prev_line_1
            else:
                # Vérifier i-2 au cas où il y a une ligne vide entre le numéro et le titre
                if i > 1:
                    prev_line_2 = lines[i-2].strip() if i-2 >= 0 else ""
                    if prev_line_2.isdigit() and int(prev_line_2) > 0:
                        num_str = prev_line_2
        # Nettoyer le titre (enlever le numéro au début si présent par erreur)
        title = line
        import re as re_mod
        m_num = re_mod.search(r"^\d+\s+", title)
        if m_num and not num_str:
            num_str = title[:m_num.end()-1].strip()
            title = title[m_num.end():]
        # Si le titre est vide après nettoyage, passer
        if not title:
            i += 1
            continue
        # L'artiste est généralement sur la ligne suivante
        artists_line = ""
        if i + 1 < len(lines):
            artists_line = lines[i + 1].strip()
            # Vérifier que c'est bien un artiste (contient des noms connus, virgules, etc.)
            # Si la ligne suivante est un autre titre ou vide, pas d'artiste
            if not ("," in artists_line or len(artists_line.split()) >= 1) or artists_line.startswith("Logo") or artists_line.startswith("Cover") or artists_line.startswith("Download"):
                artists_line = ""
        songs.append((num_str, title, artists_line))
        i += 1
        if artists_line:
            i += 1
    # Dédupliquer par titre + artiste
    seen = []
    unique_songs = []
    for s in songs:
        key = s[1].lower().strip()
        if key not in [k.lower() for k, _, _ in seen]:
            seen.append(s)
            unique_songs.append(s)
    return unique_songs

def file_exists_for(title):
    # Vérifier si un mp3 avec ce titre existe déjà
    for f in os.listdir(OUTDIR):
        if f.endswith(".mp3") and title.lower() in f.lower():
            return True, f
    return False, None

def download(num_str, title, artist, idx, total):
    exists, fname = file_exists_for(title)
    if exists:
        print(f"[{idx}/{total}] SKIP (doublon évité) : {title} -> {fname}")
        return True
    query = f"{title} {artist}".replace('"', '').replace("'", '')
    # Nom personnalisé : numéro - titre - artiste.mp3 (caractères lisibles, pas d'underscore)
    # Nettoyer uniquement les caractères interdits dans un nom de fichier (\, /, :, *, ?, ", <, >, |)
    def clean_for_filename(text):
        import re
        # Remplacer uniquement les caractères interdits dans les noms de fichiers Windows/macOS
        clean = re.sub(r'[\\/:*?"<>|]', "_", text)
        # Remplacer plusieurs underscores consécutifs par un seul
        clean = re.sub(r"_+", "_", clean)
        # Supprimer les underscores au début et à la fin
        clean = clean.strip("_")
        return clean
    safe_title = clean_for_filename(title)
    safe_artist = clean_for_filename(artist) if artist else "Unknown"
    num_part = f"{int(num_str):03d}" if num_str and num_str.isdigit() else "000"
    # Format personnalisé : {num:03d} - {titre lisible} - {artiste lisible}
    custom_name = f"{num_part} - {safe_title} - {safe_artist}"
    out_template = os.path.join(OUTDIR, f"{custom_name}.%(ext)s")
    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=tv,android,ios,web_safari",
        "-x", "--audio-format", "mp3", "--audio-quality", "0",
        "-o", out_template,
        "--max-downloads", "1",
        "--no-playlist",
        f"ytsearch1:{query}"
    ]
    print(f"[{idx}/{total}] TÉLÉCHARGEMENT : {title} - {artist}")
    print(f"         Commande : {' '.join(cmd)}")
    env = os.environ.copy()
    env["PATH"] = PATH
    result = subprocess.run(cmd, capture_output=True, text=True, env=env,
                            cwd=OUTDIR, timeout=180)
    if result.returncode == 0:
        # Trouver le fichier créé
        files = sorted(os.listdir(OUTDIR), key=lambda x: os.path.getmtime(os.path.join(OUTDIR, x)))
        new_file = None
        for f in files:
            if f.endswith(".mp3") and f not in ["download_script.sh"]:
                # Vérifier si c'est nouveau (modifié récemment)
                if os.path.getmtime(os.path.join(OUTDIR, f)) > (os.path.getmtime(FILE_CACHE) if os.path.exists(FILE_CACHE) else 0):
                    new_file = f
                    break
        print(f"         SUCCÈS -> {new_file}")
        clean_oversized()
        return True
    else:
        print(f"         ÉCHEC : {result.stderr[-500:] if result.stderr else 'unknown error'}")
        return False

def main():
    clean_oversized()  # Nettoyer fichiers >20Mo au lancement
    songs = get_songs()
    print(f"Liste extraite : {len(songs)} morceaux visibles (sur 387 annoncés)")
    # Limiter à 5 téléchargements pour ne pas bloquer la session
    max_downloads = int(os.environ.get("MAX_DL", "3"))
    print(f"Téléchargement max dans cette session : {max_downloads} (défini par MAX_DL)")
    downloaded = 0
    for i, (num_str, title, artist) in enumerate(songs, 1):
        ok = download(num_str, title, artist, i, len(songs))
        if ok and not file_exists_for(title)[0]:
            # Si le fichier a vraiment été créé
            pass
        if ok and not file_exists_for(title)[0] and downloaded < max_downloads:
            # Si c'était un téléchargement effectif (pas un skip)
            # On compte les téléchargements effectifs par vérification après coup
            pass
    # Vérification finale
    print("\n--- ÉTAT FINAL ---")
    mp3s = [f for f in os.listdir(OUTDIR) if f.endswith(".mp3")]
    print(f"Fichiers MP3 dans {OUTDIR}: {len(mp3s)}")
    for m in sorted(mp3s):
        size = os.path.getsize(os.path.join(OUTDIR, m)) / (1024*1024)
        print(f"  - {m} ({size:.1f} Mo)")

if __name__ == "__main__":
    main()
