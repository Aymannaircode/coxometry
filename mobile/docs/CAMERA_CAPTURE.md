# Capture caméra / négatoscope — MVP Option B

Flux d’acquisition photo pour radiographie sur négatoscope (prototype).

## Workflow

1. Accueil → **Prendre une photo**
2. Écran de **guidage** (cadre visuel + consignes + avertissement prototype)
3. Ouverture de la **caméra système** (`image_picker` / `ImageSource.camera`)
4. Écran de **confirmation** : aperçu + **Utiliser cette photo** / **Reprendre**
5. **Utiliser** → même chemin que la galerie : Aperçu → Analyser → `POST /analyze` → Résultats / PDF

L’import galerie (**Importer une image**) est inchangé.

## Guidage de cadrage

- Cadre décoratif (coins) sur l’écran de guidage et en overlay sur l’aperçu capturé
- **N’altère pas** l’image (pas de crop, pas de correction de perspective)
- Ce n’est **pas** une limite de mesure clinique

La caméra système ne permet pas un overlay live in-app sans package `camera` dédié (hors scope Option B). Le cadre aide avant capture et sur l’aperçu.

## Pipeline d’analyse

Après confirmation, les octets suivent **exactement** le chemin galerie :

`EXIF bake` → `PreviewScreen` → `/analyze` → V2/V5 → QC → géométrie → Résultats → PDF

Aucun second pipeline d’inférence.

## Limitations (à lire)

| Validé aujourd’hui | Pas encore validé |
|--------------------|-------------------|
| Dataset DICOM→PNG (`new_26`) | Photos téléphone |
| Pipeline V5 + mesures VCE / Tönnis / CCD | Photos de négatoscope |
| Import image numérique | Performance sous reflets / perspective |
| UI/workflow caméra (écrans + tests unitaires) | Matériel caméra Android réel |

**Ne pas** présenter cette fonctionnalité comme cliniquement validée pour les photos de radiographies.

**Démo sans téléphone :** utiliser le chemin import numérique documenté dans [README.md](../README.md) (section « Chemin de démo recommandé »). L’émulateur peut ouvrir une caméra virtuelle, mais cela **ne valide pas** un appareil physique ni un négatoscope.

## Validation appareil physique

Le build APK **ne valide pas** la caméra. Sur un **téléphone Android réel**, tester :

- autorisation caméra (accorder / refuser)
- ouverture caméra et capture
- aperçu, reprendre, utiliser
- orientation EXIF
- cadrage radiographie complète, reflets, netteté
- upload, analyse, résultats, export PDF

Procédure E2E générale : [TEST_MOBILE_E2E.md](TEST_MOBILE_E2E.md).
