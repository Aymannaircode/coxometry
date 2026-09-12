# `mvp_geometry` — Calcul géométrique des mesures coxométriques MVP

Module Python **autonome** (bibliothèque standard uniquement) qui calcule les
trois mesures du MVP à partir de coordonnées de landmarks :

- **VCE / Wiberg (LCEA)** ;
- **angle de Tönnis** ;
- **angle CCD** (caput-collum-diaphysaire / neck-shaft).

Les définitions suivent `docs/landmark_specification.md` (section 3).

> Aucune IA, aucune inférence, aucun entraînement, aucun modèle. Les
> coordonnées proviennent **exclusivement** d'une saisie manuelle ou de tests
> synthétiques. Le module **lit** éventuellement les JSON du pilote mais n'écrit
> jamais et n'accède pas à `Dataset1/`.

## Conventions

- Coordonnées en **pixels image**, origine coin supérieur gauche, axe `y` vers
  le bas.
- Radiographie **AP bassin** : droite patient à **gauche** de l'image
  (`*_R` à gauche, `*_L` à droite).
- Angles en **degrés**.

### Définitions retenues

| Mesure | Construction | Landmarks |
|--------|--------------|-----------|
| VCE | angle entre la verticale (⟂ à `ITH = TD_R–TD_L`, par `FHC`) et `FHC→ASL` | `TD_R`, `TD_L`, `FHC`, `ASL` |
| Tönnis | angle entre l'horizontale (∥ `ITH`, par `ASM`) et `ASM→ASL` | `TD_R`, `TD_L`, `ASM`, `ASL` |
| CCD | angle médial entre l'axe col `FHC→FNM` et l'axe diaphyse `FSP→FSD` | `FHC`, `FNM`, `FSP`, `FSD` |

### Conventions de signe

- **VCE** : positif quand `ASL` est **latéral** à la verticale (couverture
  normale) ; négatif en sous-couverture (bord médial à la verticale).
- **Tönnis** : positif quand le sourcil **s'incline vers le bas en latéral**
  (dysplasie typique) ; négatif si le toit remonte en latéral.
- **CCD** : angle médial dans `[0, 180]°` (normal ~120–135°).

La verticale (VCE) et l'horizontale (Tönnis) sont définies **relativement à la
droite inter-teardrop** : une inclinaison pelvienne modérée (< 90°) ne change
donc pas ces mesures (testé). Le CCD ne dépend d'aucune référence externe et
est invariant par toute rotation. Les seuils cliniques (normal / dysplasie) ne
sont **pas** figés ici (ambiguïté A4, à valider avec le référent médical).

## Utilisation

### En ligne de commande (lecture seule)

```powershell
# Démonstration synthétique (hanche droite : VCE 25°, Tönnis 10°, CCD 130°)
python -m mvp_geometry.cli --demo

# À partir de coordonnées manuelles "NOM=x,y;..." (v=2 implicite)
python -m mvp_geometry.cli --manual "TD_R=300,500;TD_L=500,500;FHC_R=436.6,495.7;ASL_R=394.3,405.1"

# À partir d'un JSON pilote (schéma mvp-pilot-1.0) — aucun fichier n'est modifié
python -m mvp_geometry.cli --json annotation_pilot/annotations/annotator_A/P01_a308.json
```

### En bibliothèque

```python
from mvp_geometry import vce_angle, tonnis_angle, ccd_angle

vce = vce_angle(td_r, td_l, fhc, asl, side="R")
tonnis = tonnis_angle(td_r, td_l, asm, asl, side="R")
ccd = ccd_angle(fhc, fnm, fsp, fsd)
```

Couche haut niveau à partir d'un schéma pilote :

```python
from mvp_geometry import load_pilot_schema, landmarks_by_name, compute_all_sides

schema = load_pilot_schema("annotation_pilot/annotations/annotator_A/P01_a308.json")
results = compute_all_sides(landmarks_by_name(schema))
print(results["R"].vce, results["R"].ccd)
```

Seuls les landmarks `v=2` (point net posé par clic humain) sont exploités ;
`v=0`/`v=1`/`null` rendent la mesure concernée « indisponible » avec une raison,
sans jamais inventer de coordonnée.

## Cas limites gérés

Une `GeometryError` est levée (et rapportée comme mesure indisponible par la
couche haut niveau) lorsque :

- `TD_R` = `TD_L` (référence horizontale indéterminée) ;
- `FHC` = `ASL` (direction de couverture indéterminée) ;
- `ASM` = `ASL` (sourcil indéterminé → Tönnis non défini) ;
- `FHC` = `FNM` (axe du col indéterminé) ;
- `FSP` = `FSD` (axe diaphysaire indéterminé).

## Tests

```powershell
python -m unittest mvp_geometry.tests.test_measurements -v
```

Les cas nominaux sont **construits analytiquement** à partir d'angles cibles
connus (valeurs attendues exactes). La suite vérifie aussi l'invariance par
translation / échelle / rotation modérée, les signes, et les cas dégénérés.

## Fichiers

| Fichier | Rôle |
|---------|------|
| `measurements.py` | Primitives + `vce_angle`, `tonnis_angle`, `ccd_angle` |
| `landmarks.py` | Lecture seule du schéma `mvp-pilot-1.0` |
| `hip_measures.py` | Calcul par hanche + gestion des landmarks manquants |
| `cli.py` | Interface ligne de commande (`--demo`, `--manual`, `--json`) |
| `tests/test_measurements.py` | Tests analytiques |
