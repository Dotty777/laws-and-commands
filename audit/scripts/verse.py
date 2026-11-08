"""Print Saints Translation text: python3 -I /home/claude/work/verse.py "Book ch:v[-v]" [more refs...]"""
import sys
sys.path.insert(0, "/home/claude/work")
from audit_lib import Bible
B = Bible()
for ref in sys.argv[1:]:
    idx, p = B.expand(ref)
    if p: print("!!", p)
    for i in idx: print(f"{B.label(i)}  {B.verses[i]['text']}")
    print()
