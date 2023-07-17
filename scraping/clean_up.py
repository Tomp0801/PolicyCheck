import sys
from adapters import RedditAdapter, GoogleAdapter

file = sys.argv[1]
type = sys.argv[2]
save_file = sys.argv[3]


if type=="reddit":
    adap = RedditAdapter(file)
elif type=="google":
    adap = GoogleAdapter(file)
adap.save(save_file)

