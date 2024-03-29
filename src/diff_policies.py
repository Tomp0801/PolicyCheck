import sys
from scraping.adapters import RedditAdapter, GoogleAdapter
from diffing.diff_marking import Differ

type = sys.argv[1]

if type=="reddit":
    files = ["examples/html/reddit/2018-09-24.html", "examples/html/reddit/2020-10-15.html"]
elif type=="google":
    files = ["examples/html/google/2020-03-31.html", "examples/html/google/2022-01-05.html"]

save_files = ["tmp/old.html", "tmp/new.html"]

for (in_file, out_file) in zip(files, save_files):
    if type=="reddit":
        adap = RedditAdapter(in_file, sectionize=True, wrap_text=False)
    elif type=="google":
        adap = GoogleAdapter(in_file)
    adap.save(out_file)

differ = Differ(save_files[0], save_files[1], 
                F=0.5, ratio_mode='accurate',
                use_replace=True)
differ.save("tmp/diff.html")
