# Revue ASL / ASM — new_26

Galerie dédiée à la vérification manuelle des landmarks **ASL** et **ASM** (sourcil acétabulaire).

## Ouvrir la galerie

```
datasets/yolo_pose_new_26/visual_check/asl_asm_review/index.html
```

## Contenu

- **26 zooms** (acétabulum droit + gauche par cas)
- Points **ASL** / **ASM** colorés (orange=R, bleu=L)
- Ligne **ASL → ASM**
- Références grises **FHC** et **TD** (contexte anatomique, non modifiés)

## Rapports

- `asl_asm_report.csv` — coordonnées et métriques
- `asl_asm_report.md` — tableau lisible + cas signalés

## Heuristique « suspect »

**3** cas signalés automatiquement pour revue prioritaire.
Ce flag **ne remplace pas** votre validation manuelle et **ne modifie aucune annotation**.

## Checklist manuelle

- [ ] ASL est sur l'extrémité **latérale** du sourcil (pas sur l'aile iliaque)
- [ ] ASM est sur l'extrémité **médiale** du sourcil
- [ ] La ligne ASL→ASM suit le **toit acétabulaire porteur**
- [ ] Les points ne sont pas **trop hauts** sur l'ilium
- [ ] R/L non inversés (ASL latéral à ASM sur chaque côté)

## Regénérer

```bash
.venv\\Scripts\\python.exe annotation_pilot\\scripts\\analyze_asl_asm_new_26.py
```
