#!/usr/bin/env python
# -*- coding: utf-8 -*-
from graia.application.friend import Friend
from role import role
import random
import numpy

g_value = {"vote": 0, "cupid": 0, "vote_r": "投票结果\n", "police": "投票结果\n"}

setting = [3, 0, 3, 1, 1, 1, 0]
setting_v = [3, 0, 3, 1, 1, 1, 0]
setting_all = 9
set_value = ["狼人", "白狼王", "村民", "预言家", "女巫", "猎人", "丘比特"]
# alive = {}  # 0
wolf = {}  # 1
# illager = {}  # 2
# cupid = {}  # 3
users = []
dead = {}  # 4
stage = 0
ran = []
vote = []
vote_every_one = []
if_alive = []
rule = [0, 0]
one_night_dead = []  # 1yes 2no 0alive
police = []
if_police = []
vote_police = []
if_vote_police = []


class gol:

    def __init__(self):
        pass

    # 标准全局变量的取用
    def set(self, name, value):
        global g_value
        g_value[name] = value

    def get(self, name, defValue=None):
        try:
            return g_value[name]

        except KeyError:
            return defValue

    # 设置的修改
    def set_setting_1(self, s):
        global setting, setting_all, setting_v
        if int(s[1]) < 7:
            setting_all = setting_all - setting[int(s[1])] + int(s[2])
            setting[int(s[1])] = int(s[2])
            setting_v[int(s[1])] = int(s[2])

    def set_setting_all(self, s):
        global setting, setting_all
        l = len(s)
        if len(s) > len(setting):
            l = len(setting) + 1
        for i in range(1, l):
            setting_all = setting_all - setting[i - 1] + int(s[i])
            setting[i - 1] = int(s[i])
            setting_v[i - 1] = int(s[i])

    def print_setting(self):
        s = str(setting_all) + "人局：\n\t"
        for num in range(0, 7):
            if setting[num] > 0:
                s += str(set_value[num]) + str(setting[num]) + "个\n\t"

        return s

    def get_set_value(self):
        return set_value

    def judge_if_have(self, identity):
        if setting[identity] != 0:
            return 1
        else:
            return 0

    def judge_by_identity(self, identity):
        flag = [-1, 0]
        if setting_v[identity] != 0:
            for i in range(0, len(users)):
                if users[i].get_identity() == identity:
                    flag[0] = i
                    flag[1] = users[i]
        return flag

    # 全部参赛者编号
    def append_all(self, r: role):
        global users
        users.append(r)

    def findin_all(self, friend: Friend):
        id = friend.id
        flag = [-1, 0]

        for i in range(0, len(users)):
            if users[i].get_friend().id == id:
                flag[0] = i
                flag[1] = users[i]
        return flag

    def full_all(self):
        return setting_all - len(users)

    def get_all(self):
        return users

    def print_all(self):
        s = "参赛者："
        for i in range(0, len(users)):
            s += "\n编号" + str(i + 1) + "昵称" + users[i].get_friend().nickname
        return s

    def get_one_bynum(self, num):
        return users[int(num) - 1]

    # 游戏阶段变更
    def stage_add(self):
        global stage
        # print("1"+str(stage))
        stage = stage + 1
        # print("2"+str(stage))

    def stage_set(self, st):
        global stage
        stage = st

    def stage_get(self):
        return stage

    # 身份随机数
    def identity_random(self):
        global ran
        ran = random.sample(range(1, setting_all + 1), setting_all)
        # print(ran)
        for i in range(0, len(users)):
            identity = 0
            for j in range(0, len(setting)):
                identity += setting[j]
                # (ran[i])
                # print(identity)
                # print("\n")
                if ran[i] <= identity:
                    users[i].set_identity(j)
                    break

    def reset(self):
        global users
        global stage, g_value
        global setting_v, setting_all, wolf
        users = []
        stage = 0
        setting_v = setting
        setting_all = 0
        for i in range(0, len(setting)):
            setting_all += setting[i]

        g_value = {"vote": 0, "cupid": 0, "vote_r": "投票结果\n", "police": "投票结果\n"}
        wolf = {}

    def add_list(self, list_name, role_num, r):

        if list_name == 1:
            global wolf
            wolf[role_num] = r
        if list_name == 2:
            global villager
            villager[role_num] = r
        if list_name == 3:
            global cupid
            cupid[role_num] = r
        if list_name == 4:
            global dead
            dead[role_num] = r

    def get_list(self, list_name):

        if list_name == 1:
            return wolf

        if list_name == 2:
            return villager

        if list_name == 3:
            return cupid

        if list_name == 4:
            return dead

    # temp方法
    def union_show(self):
        return if_alive

    # 投票部分
    def init_if_alive(self):
        global if_alive

        if_alive = [1 for x in range(0, len(users))]

    def init_vote(self):
        global vote
        vote = [0 for x in range(0, len(users))]

    def vote_one(self, i: int):
        global vote
        vote[i - 1] += 2

    def get_vote_result(self):
        m = 0
        result = [-1]  # 全员弃票
        for i in range(0, len(vote)):
            print(vote[i])
            print(if_alive[i])
            if vote[i] * if_alive[i] > m:
                m = vote[i] * if_alive[i]
                result = []
                result.append(i + 1)
            elif vote[i] * if_alive[i] == m:
                result.append(i + 1)  # 平票
        return result

    def set_if_alive(self, i: int):
        global if_alive
        if_alive[i] = 0

    def get_if_alive(self):
        return if_alive

    def die(self, num: int):
        global setting_v
        setting_v[num] -= 1

    def reset_dead(self):
        global dead
        dead = {}

    def set_one_night_dead(self, num: int, value: int):
        global one_night_dead
        one_night_dead[num] = value

    def init_one_night_dead(self):
        global one_night_dead
        one_night_dead = [0 for x in range(0, len(users))]

    def get_one_night_dead(self):

        return one_night_dead

    def set_rule(self, i: int, j: int):
        global rule
        rule[i] = j

    def get_rule(self):
        return rule

    def add_vote_result(self, st, key):
        global g_value
        st = g_value[key] + st
        g_value[key] = st

    def get_vote_info(self):
        return g_value["vote_r"]

    def reset_vote_r(self):
        global g_value
        g_value["vote_r"] = ""

    def reset_police(self):
        global g_value
        g_value["police"] = ""

    def init_vote_every_one(self):
        global vote_every_one
        vote_every_one = [0 for i in range(0, len(users))]

    def vote_every_one(self, i: int):
        global vote_every_one
        vote_every_one[i] = 1

    def judge_vote_every_one(self, i: int):
        if vote_every_one[i] == 1:
            return 1
        else:
            return 0

    def init_police(self):
        global police, vote_police, if_vote_police,if_police
        police = [0 for i in range(0, len(users))]
        vote_police = [0 for i in range(0, len(users))]
        if_vote_police = [0 for i in range(0, len(users))]
        if_police = [0 for i in range(0, len(users))]

    # 参选
    def police(self, i: int):
        global police
        police[i] = 1

    # 判断是否参选
    def if_police(self, i: int):
        if police[i] == 1:
            return 1
        else:
            return 0
    def get_police(self):
        return police

    def set_if_police(self,i:int):
        global if_police
        if_police[i]=1

    # 投票
    def vote_police(self, j: int):
        global vote_police
        vote_police[j] += 1

    # 投票结果
    def get_police_result(self):
        m = 0
        result = [-1]  # 全员弃票
        for i in range(0, len(vote_police)):
            #print(vote_police[i])
            #print(police[i])
            if vote_police[i] * police[i] > m:

                m = vote_police[i] * police[i]
                result = []
                result.append(i + 1)
            elif vote_police[i] * police[i] == m:
                result.append(i + 1)  # 平票
        return result

    def this_one_vote_police(self, i: int):
        global if_vote_police
        if_vote_police[i] = 1

    def if_vote_police(self, i: int):
        if if_vote_police[i] == 1:
            return 1
        else:
            return 0

    def add_vote_police(self, st):
        global g_value
        g_value["police"] = g_value["police"] + st

    def get_police_info(self):
        return g_value["police"]

    def vote_as_police(self, i: int):
        global vote
        vote[i] += 3

    def setpolice(self,i:int):
        global users
        users[i].set_police()
