import os, shutil
root = os.getcwd()
remove_files = [
    "_ngsl_site.html", "_ngsl_s140.html",
    "_parse_xlsx.py", "_parse_html.py",
    "_todo1.txt","_todo2.txt","_todo3.txt","_todo4.txt",
    "_todo5.txt","_todo6.txt","_todo7.txt","_todo8.txt",
    "ngsl_missing.json",
    "_live_v35.html", "_live_check.html",
]
remove_dirs = ["_ngsl_raw"]
for f in remove_files:
    p = os.path.join(root, f)
    if os.path.exists(p):
        os.remove(p); print("rm file:", f)
    else:
        print("skip (absent):", f)
for d in remove_dirs:
    p = os.path.join(root, d)
    if os.path.isdir(p):
        shutil.rmtree(p); print("rm dir:", d)
    else:
        print("skip (absent):", d)
# what remains (top-level, non-hidden)
keep = sorted(x for x in os.listdir(root) if not x.startswith('.') and os.path.isfile(os.path.join(root,x)))
print("\nremaining top-level files:")
for x in keep: print(" ", x)
