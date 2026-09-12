# Rapport PDF — export depuis l'application

## Générer un rapport

1. Lancer le backend démo V5 si besoin : `.\backend\run_demo.ps1`
2. Ouvrir l'app Flutter et analyser une radiographie
3. Sur l'écran **Résultats**, appuyer sur **Exporter le rapport**
4. Le PDF est généré localement puis proposé via la feuille de partage système

## Emplacement du fichier

Le PDF est enregistré dans le répertoire documents de l'application :

- Android / iOS : `getApplicationDocumentsDirectory()` (espace privé de l'app)
- Nom : `rapport_coxometrie_YYYYMMDD_HHMMSS.pdf`

Le partage système permet ensuite d'enregistrer dans Téléchargements, Drive, e-mail, etc.

## Contenu

Le rapport A4 inclut :

- en-tête (Coxométrie, titre, date de génération, modèle V2 / V5 Phase 2)
- radiographie + overlay landmarks (même géométrie que l'écran Résultats)
- statut de présentation existant
- mesures VCE / Tönnis / CCD (valeurs déjà calculées — pas de recalcul)
- qualité IT (si V5) : Accepté / À revoir / Indisponible + motifs FR
- avertissements QC / mesures manquantes existants
- avertissement non diagnostique

Aucune identité patient n'est inventée.

## Limites plateforme

| Plateforme | Notes |
|---|---|
| Android | Cible principale ; partage PDF via `share_plus` |
| iOS | Code Dart portable ; projet `ios/` à générer sur Mac |
| Windows | Génération + partage / ouverture selon apps installées |
| Polices | Polices système (Arial/Roboto…) pour accents FR ; sinon Helvetica |

## Dépendances

- `pdf`
- `path_provider`
- `share_plus`

Pas de package `printing` (prévisualisation native non requise).
