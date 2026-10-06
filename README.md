# Mir Sladostey — storefront demo

Static copy of mirsladostey164.ru with the new skin applied: https://vdolesov.github.io/

The live site runs on 1C-Bitrix with the Aspro Max template. The demo keeps its pages, URLs and markup and changes the visual layer; a few demo scripts stand in for the backend (cart, search, forms).

## Layout

| Path | Contents |
| --- | --- |
| `index.html`, `catalog/`, `basket/`, `company/`, `contacts/`, `help/`, `info/`, … | site pages at their original URLs, built by `skin/build_site.py` |
| `skin/` | the skin, demo scripts and build tools — see [skin/README.md](skin/README.md) |
| `assets/` | product photos, hero slides, contacts photo |
| `vendor/` | template stylesheets, scripts, bundles and images served from this site, so the pages do not depend on mirsladostey164.ru |
| `build/` | catalog snapshot, source photos and photo pipelines |
| `v1/`, `v2/` | earlier versions: the July storefront and the September rebuild |
| `404.html` | not found page |

## Earlier versions

`v1/` (https://vdolesov.github.io/v1/) and `v2/` (https://vdolesov.github.io/v2/) are snapshots exported from history with `python skin/export_version.py <commit> <name>`. `v1/` also carries the store map and footer of the current site (`v1/bottom.css`, `v1/bottom.js`), applied by `python skin/v1_bottom.py`; re-run it after re-exporting. Its product photos are series v10 (`build/v1_photos.py`), the Ossetian pies come from `build/pies_v1.py` and the wide hero from `build/v1_hd.py`.

## Requirements

Python 3.11 with Pillow and NumPy for the site build; the photo pipelines also need OpenCV and rembg.
