import os,sys
import numpy as np

def get_run(runs):
    rlist = []
    if not isinstance(runs,str):
        return rlist
    for each in runs.split(","):
        if each == "":
            continue
        elif ":" in each:
            start,end = each.split(":")
            rlist.extend(range(int(start),int(end)+1))
        elif "-" in each:
            start,end = each.split("-")
            rlist.extend(range(int(start),int(end)+1))
        else:
            rlist.append(int(each))
    return rlist


