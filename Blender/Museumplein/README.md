# Museumplein skatepark

Open `museumplein.blend` in Blender 5.2 or newer. This is the editable source asset, with all image textures packed in the file. It is versioned with Git LFS; run `git lfs pull` after cloning.

The scene contains approximately 4.13 million vertices. Coordinates are metric, but dimensions are inferred from photographs rather than surveyed. The latest revision fixes the rounded quarterpipe returns, its rounded rear platform, and the raised court-side coping.

- `review/index.html`: reference comparison, detail renders, and a full-plan opacity comparison.
- `validation.json`: fresh-file geometry checks and local quality assessment.
- `tools/validate.py`: recheck the opened scene.
- `tools/render.py`: regenerate the saved inspection views.
- `../../Museumplein/`: original local reference photographs, preserved but excluded from Git. The review includes the top-view reference.

Run from the repository root:

```sh
blender -b Blender/Museumplein/museumplein.blend --python Blender/Museumplein/tools/validate.py
blender -b Blender/Museumplein/museumplein.blend --python Blender/Museumplein/tools/render.py
```

The `.blend` is the source of truth. Obsolete incremental construction scripts and intermediate `.blend` files have been removed; rebuilding from photographs is not automated by these maintenance tools.

## Assessment

| Revision | Round returns | Coping contact | Local plan agreement | Overall photo fidelity |
| --- | ---: | ---: | ---: | ---: |
| 28 | 9.3 | 9.2 | 8.5 | 8.5 |
| 29 | 9.3 | 9.2 | 9.0 | 8.5 |

These are visual self-assessments, not measured reconstruction accuracy. The full plan still differs in material wear, surroundings, and some transitions. It is not an exact photographic duplicate.
