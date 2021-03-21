# import os
# import time
import datetime
from gol import gol
import random
import time


def main():
    g = gol()
    g.set("x", 1)
    s = g.get("x")
    print(f"{s}")


def gen(n):
    return random.sample(range(1, n + 1), n)


def array():
    a = ["狼人", "村民", "预言家", "女巫", "猎人", "丘比特", "白狼王"]
    a.append(1)
    a.append(2)

    print(a)


def test():
    g = {"ok": "ok", "ok1": "ok1"}
    return g.items()


def numtest():
    s = [0, "ok"]
    print(int(s[1]))


if __name__ == '__main__':
    # p = gen(9)
    # print(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8])
    # print(__name__)
    # test()
    # main()
    # di = {'Google': 'www.google.com', 'Runoob': 'www.runoob.com', 'taobao': 'www.taobao.com'}
    # for key, values in di.items():
    #    print(key, values)
    # di["vote"]=0
    # if di["vote"]==0:
    # print("ok")
    # print(len(di.items()))
    #numtest()

