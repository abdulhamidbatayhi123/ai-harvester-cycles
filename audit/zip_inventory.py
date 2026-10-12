import sys, zipfile, collections, posixpath
sys.stdout.reconfigure(encoding="utf-8")
z = zipfile.ZipFile(sys.argv[1])
infos = [i for i in z.infolist() if not i.is_dir()]
print("files", len(infos), "uncompressed MB", round(sum(i.file_size for i in infos)/1e6,1))
ext = collections.Counter(posixpath.splitext(i.filename)[1].lower() for i in infos); print(ext.most_common())
dirs = collections.defaultdict(lambda: [0,0])
depth = int(sys.argv[2]) if len(sys.argv)>2 else 3
for i in infos:
    d = "/".join(i.filename.split("/")[:depth])
    dirs[d][0]+=1; dirs[d][1]+=i.file_size
for d,(n,s) in sorted(dirs.items()): print(f"{n:5d} {s/1e6:8.1f}MB  {d}")
