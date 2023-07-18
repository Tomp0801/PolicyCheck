import sys
from diff_marking import diff_mark_file

old_file = sys.argv[1]
new_file = sys.argv[2]
save_file = sys.argv[3]

diff_mark_file(old_file, new_file, save_file)
