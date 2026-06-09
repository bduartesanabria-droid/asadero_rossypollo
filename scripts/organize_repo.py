"""
Organize repository files into the expected layout for the Flask app.

Usage:
  python scripts/organize_repo.py --apply

By default the script performs a dry-run and prints the planned operations.
Pass `--apply` to actually move files.

What it does:
 - Moves top-level `static/img/*` -> `app/static/img/`
 - Moves top-level `static/icon.svg` -> `app/static/icon.svg`
 - Moves any top-level JS/CSS files into `app/static/js` and `app/static/css` if present
 - Leaves Dockerfiles, README, migrations, tests and app/ untouched

Run this from the repository root.
"""

import os
import shutil
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
DRY_RUN = True

moves = []
# Static images
src_static = os.path.join(REPO_ROOT, 'static')
dst_static = os.path.join(REPO_ROOT, 'app', 'static')
if os.path.isdir(src_static):
    img_src = os.path.join(src_static, 'img')
    if os.path.isdir(img_src):
        for fname in os.listdir(img_src):
            srcf = os.path.join(img_src, fname)
            destf = os.path.join(dst_static, 'img', fname)
            moves.append((srcf, destf))
    icon = os.path.join(src_static, 'icon.svg')
    if os.path.exists(icon):
        moves.append((icon, os.path.join(dst_static, 'icon.svg')))

# Top-level js/css
for fname in os.listdir(REPO_ROOT):
    if fname.endswith('.js'):
        moves.append((os.path.join(REPO_ROOT, fname), os.path.join(dst_static, 'js', fname)))
    if fname.endswith('.css'):
        moves.append((os.path.join(REPO_ROOT, fname), os.path.join(dst_static, 'css', fname)))


def apply_moves(apply=False):
    for src, dst in moves:
        if not os.path.exists(src):
            print('SKIP (missing):', src)
            continue
        print(('MOVE' if apply else 'DRYRUN'), src, '->', dst)
        if apply:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
    # remove empty top-level static dir
    if apply and os.path.isdir(src_static):
        try:
            shutil.rmtree(src_static)
            print('Removed directory', src_static)
        except Exception as e:
            print('Could not remove', src_static, e)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true', help='Apply the moves')
    args = p.parse_args()
    apply_moves(apply=args.apply)
    if args.apply:
        print('Organization applied. Run your tests to verify.')
    else:
        print('\nDry-run complete. To apply: python scripts/organize_repo.py --apply')
