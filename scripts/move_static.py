import os, shutil
root = os.path.dirname(os.path.dirname(__file__))
src_dir = os.path.join(root, 'static')
dst_dir = os.path.join(root, 'app', 'static')
if not os.path.isdir(src_dir):
    print('No hay directorio static/ en la raíz, nothing to move')
    raise SystemExit(0)
# move img/*
img_src = os.path.join(src_dir, 'img')
if os.path.isdir(img_src):
    for fname in os.listdir(img_src):
        srcf = os.path.join(img_src, fname)
        destf = os.path.join(dst_dir, 'img', fname)
        os.makedirs(os.path.dirname(destf), exist_ok=True)
        print('Moving', srcf, '->', destf)
        shutil.move(srcf, destf)
# move icon.svg
icon = os.path.join(src_dir, 'icon.svg')
if os.path.exists(icon):
    dest_icon = os.path.join(dst_dir, 'icon.svg')
    os.makedirs(os.path.dirname(dest_icon), exist_ok=True)
    print('Moving', icon, '->', dest_icon)
    shutil.move(icon, dest_icon)
# remove source static dir if empty
try:
    shutil.rmtree(src_dir)
    print('Removed', src_dir)
except Exception as e:
    print('Could not remove', src_dir, e)
