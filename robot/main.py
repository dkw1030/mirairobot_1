import asyncio
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication
from graia.application.message.elements.internal import At, Plain
from graia.application.session import Session
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from graia.broadcast.interrupt import *
from graia.application.interrupts import GroupMessageInterrupt
from graia.application.interrupts import FriendMessageInterrupt

from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, OptionalParam, RequireParam
from graia.application.friend import Friend
from gol import gol
from role import role
import role

mutex = 0

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8080",  # 填入 httpapi 服务运行的地址
        authKey="graia-mirai-api-http-authkey",  # 填入 authKey
        account=2711561854,  # 你的机器人的 qq 号
        websocket=True  # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)
inc = InterruptControl(bcc)


@bcc.receiver("FriendMessage")
async def friend_message_listener(message: MessageChain, app: GraiaMiraiApplication, friend: Friend):
    g = gol()
    # 参加游戏
    if message.asDisplay().startswith("参加") and g.stage_get() == 2:
        if g.full_all() == 0:
            await app.sendFriendMessage(friend, MessageChain.create([
                Plain("抱歉，人数已满")
            ]))
        else:
            flag = g.findin_all(friend)
            if flag[0] == -1:
                r = role.role(friend)
                g.append_all(r)
                await app.sendFriendMessage(friend, MessageChain.create([
                    Plain("参赛者" + str(r.get_friend().id) + "你的编号为" + str(r.get_no()))
                ]))
                if g.full_all() == 0:
                    gro = g.get("group")
                    await app.sendGroupMessage(gro, MessageChain.create([
                        Plain("人齐了\n" + g.print_all() + "\n发送\"开始\"以开始游戏")
                    ]))
                    g.set("win", 0)
                    g.stage_add()
                    # 3

            else:
                await app.sendFriendMessage(friend, MessageChain.create([
                    Plain("参赛者" + str(flag[1].get_friend().id) + "已参加，编号为" + str(flag[0] + 1))
                ]))
    # 丘比特连线
    if message.asDisplay().startswith("连线") and g.stage_get() == 4:
        users=g.get_all()
        flag = g.findin_all(friend)
        if flag[1].get_identity() == 6:
            s1 = message.asDisplay().split(" ")
            if len(s1) > 2:
                if s1[1].isdigit() and s1[2].isdigit():
                    if s1[1] in range(0, len(users)) and s1[2] in range(0,len(users)):
                        a = g.get_one_bynum(s1[1])
                        b = g.get_one_bynum(s1[2])
                        a.set_link(b)
                        b.set_link(a)

                        # print("fs\n")
                        if a.get_identity() < 2 and b.get_identity() < 2:
                            a.set_union(0)
                            b.set_union(0)
                            flag[1].set_union(0)
                            g.add_list(1, a.get_no(), a)
                            g.add_list(1, b.get_no(), b)
                            g.add_list(1, flag[1].get_no(), flag[1])
                            # g.add_list(0, a.get_no(), a)
                            # g.add_list(0, b.get_no(), b)
                            # g.add_list(0, flag[1].get_no(), flag[1])
                        elif a.get_identity() > 1 and b.get_identity() > 1:
                            a.set_union(1)
                            b.set_union(1)
                            flag[1].set_union(1)
                            # g.add_list(2, a.get_no(), a)
                            # g.add_list(2, b.get_no(), b)
                            # g.add_list(2, flag[1].get_no(), flag[1])

                        else:
                            a.set_union(2)
                            b.set_union(2)
                            flag[1].set_union(2)
                            # g.add_list(3, a.get_no(), a)
                            # g.add_list(3, b.get_no(), b)
                            # g.add_list(3, flag[1].get_no(), flag[1])

                        # print("fok\n")
                        await app.sendFriendMessage(a.get_friend(), MessageChain.create([
                            Plain("你被丘比特连线，队友为" + str(s1[2]) + "号参赛者")
                        ]))
                        await app.sendFriendMessage(b.get_friend(), MessageChain.create([
                            Plain("你被丘比特连线，队友为" + str(s1[1]) + "号参赛者")
                        ]))


            # print(str(g.get_one_bynum(s1[1]).get_friend().id) + str(g.get_one_bynum(s1[1]).get_union()))
            # print(str(g.get_one_bynum(s1[2]).get_friend().id) + str(g.get_one_bynum(s1[1]).get_union()))
            # print(str(g.get_one_bynum(flag[0]).get_friend().id) + str(g.get_one_bynum(s1[1]).get_union()))
    # 狼人交流
    if g.stage_get() == 6:
        # 获取自己的编号
        no = -1
        for key, values in g.get_list(1).items():
            if values.get_friend().id == friend.id:
                no = values
        # 判断这个狼没死

        if no != -1:

            if no.get_status() == 1:
                # 将自己的消息转发给其他狼

                for key, values in g.get_list(1).items():
                    if values.get_identity() < 2 and values.get_no() != no.get_no():
                        await app.sendFriendMessage(values.get_friend(), MessageChain.create([
                            Plain(str(no.get_no()) + "说：" + message.asDisplay())
                        ]))

    # 狼杀人
    if message.asDisplay().startswith("杀人 "):
        if g.stage_get() == 6:
            # 获取自己的编号
            for key, values in g.get_list(1).items():
                if values.get_friend().id == friend.id and values.get_status() == 1:
                    st = message.asDisplay().split(" ")
                    if len(st) > 1:
                        if st[1].isdigit():
                            if st[1] in range(0, len(users)):
                                if g.judge_vote_every_one(values.get_no() - 1) == 0:
                                    g.vote_every_one(values.get_no() - 1)
                                    vote(message, 0)
                                else:
                                    await app.sendFriendMessage(values.get_friend(), MessageChain.create([
                                        Plain("您已投过票")
                                    ]))


    # prophet
    if message.asDisplay().startswith("查验 ") and g.stage_get() == 7:
        users = g.get_all()
        no = -1
        for i in range(0, len(users)):
            if users[i].get_friend().id == friend.id:
                no = users[i]
        if no != -1:
            if no.get_identity() == 3:
                st = message.asDisplay().split(" ")
                if len(st) > 1:
                    if st[1].isdigit():
                        if st[1] in range(0, len(users)):
                            result = g.get_one_bynum(int(st[1])).get_identity()
                            if result == 0:
                                await app.sendFriendMessage(friend, MessageChain.create([
                                    Plain("坏人")
                                ]))
                            else:
                                await app.sendFriendMessage(friend, MessageChain.create([
                                    Plain("好人")
                                ]))

    # 女巫
    if message.asDisplay().startswith("救 ") and g.stage_get() == 8:
        users = g.get_all()
        no = -1
        for i in range(0, len(users)):
            if users[i].get_friend().id == friend.id:
                no = users[i]
        if no != -1:
            if no.get_identity() == 4 and no.get_skill()[0] == 1:
                st = message.asDisplay().split(" ")
                if len(st)>1:
                    if st[1] == "是":
                        print("救了")
                        dead = list(g.get_list(4).items())[0][1]
                        dead.set_status(1)
                        no.set_skill(0, 0)


    if message.asDisplay().startswith("毒 ") and g.stage_get() == 9:
        users = g.get_all()
        no = -1
        for i in range(0, len(users)):
            if users[i].get_friend().id == friend.id:
                no = users[i]
        if no != -1:
            if no.get_identity() == 4 and no.get_skill()[1] == 1:
                st = message.asDisplay().split(" ")
                if len(st) > 1:
                    if st[1].isdigit():
                        if st[1] in range(0, len(users)):
                            g.add_list(4, int(st[1]) - 1, users[int(st[1]) - 1])
                            users[int(st[1]) - 1].set_status(0)
                            print(users[int(st[1]) - 1].get_status())
                            no.set_skill(1, 0)
                            print("毒杀成功")

    # toupiao
    if message.asDisplay().startswith("投票 ") and g.stage_get() == 13:
        users = g.get_all()
        no = -1
        for i in range(0, len(users)):
            if users[i].get_friend().id == friend.id:
                no = users[i]

        if no != -1:
            if g.judge_vote_every_one(no.get_no() - 1) == 0 and no.get_status() == 1:
                g.vote_every_one(no.get_no() - 1)
                st=message.asDisplay().split(" ")
                if len(st) > 1:
                    if st[1].isdigit():
                        if st[1] in range(0, len(users)):
                            if no.get_police() == 1:
                                print("3vote")
                                g.vote_as_police(int(message.asDisplay().split(" ")[1]) - 1)
                            else:
                                vote(message, 1)

                            print(str(no.get_no()))
                            g.add_vote_result(str(no.get_no()) + "投了" + message.asDisplay().split(" ")[1] + "\n",
                                              "vote_r")

            else:
                await app.sendFriendMessage(no.get_friend(), MessageChain.create([
                    Plain("您已投过票")
                ]))
    # 警长投票
    if message.asDisplay().startswith("投票 ") and g.stage_get() == 11:
        print("警长投票")
        users = g.get_all()
        no = -1
        for i in range(0, len(users)):
            if users[i].get_friend().id == friend.id:
                no = users[i]

        if no != -1:
            if g.if_vote_police(no.get_no() - 1) == 0:
                st=message.asDisplay().split(" ")
                if len(st) > 1:
                    if st[1].isdigit():
                        if st[1] in range(0, len(users)):
                            g.this_one_vote_police(no.get_no() - 1)
                            g.vote_police(int(st[1]) - 1)
                            print(int(st[1]))
                            # print(g.police)
                            g.add_vote_police(str(no.get_no()) + "投了" + message.asDisplay().split(" ")[1] + "\n")

            else:
                await app.sendFriendMessage(no.get_friend(), MessageChain.create([
                    Plain("您已投过票")
                ]))
    # 上警
    if message.asDisplay().startswith("上警") and g.stage_get() == 10:
        print("okk")
        users = g.get_all()
        no = -1
        for i in range(0, len(users)):
            if users[i].get_friend().id == friend.id:
                no = users[i]

        if no != -1:
            if g.if_police(no.get_no() - 1) == 0:

                g.police(no.get_no() - 1)
                g.set_if_police(no.get_no() - 1)
                await app.sendFriendMessage(no.get_friend(), MessageChain.create([
                    Plain("参选成功")
                ]))

            else:
                await app.sendFriendMessage(no.get_friend(), MessageChain.create([
                    Plain("您已参选")
                ]))

    # hunter
    if message.asDisplay().startswith("开枪 "):
        if g.stage_get() == 13 or g.stage_get() == 11:
            users = g.get_all()
            no = -1
            for i in range(0, len(users)):
                if users[i].get_friend().id == friend.id:
                    no = users[i]

            # print("hunter")
            # print(no.get_identity())
            # print(no.get_status())
            if no != -1:
                if no.get_identity() == 5 and no.get_status() < 0:
                    st = message.asDisplay().split(" ")
                    if len(st) > 1:
                        if st[1].isdigit():
                            if st[1] in range(0, len(users)):
                                if st[1].isdigit():
                                    users[int(st[1]) - 1].set_status(-2)  # role die

                                    g.die(int(users[int(st[1]) - 1].get_identity()))  # setting--
                                    g.set_if_alive(int(st[1]) - 1)
                                    g.set_one_night_dead(int(st[1]) - 1, 1)
                                    if users[int(st[1]) - 1].get_link() != -1:
                                        users[int(st[1]) - 1].get_link().set_status(-2)  # role die

                                        g.die(users[int(st[1]) - 1].get_link().get_identity())  # setting--
                                        g.set_if_alive(users[int(st[1]) - 1].get_link().get_no() - 1)
                                        g.set_one_night_dead(users[int(st[1]) - 1].get_link().get_no() - 1, 1)
                                    gro = g.get("group")
                                    await app.sendGroupMessage(gro, MessageChain.create([
                                        Plain(str(no.get_no()) + "为猎人，开枪带走了" + st[1] + "号\n")
                                    ]))



@bcc.receiver("GroupMessage")
async def group_message_handler(
        message: MessageChain,
        app: GraiaMiraiApplication,
        group: Group, member: Member,
):
    # 全局变量存储
    g = gol()
    # 设置部分
    # 设定游戏在该群进行
    if message.asDisplay().startswith("gset") and g.stage_get() == 0:
        if member.id == 2803309546 or member.id == 471608262:
            g.set("group", group)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("已指定本群")
            ]))
            g.stage_add()
            # 此时stage变量为1
    if message.asDisplay().startswith("setall") and g.stage_get() < 2:
        if member.id == 2803309546 or member.id == 471608262:
            s = message.asDisplay().split(" ")
            g.set_setting_all(s)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(g.print_setting())
            ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id), Plain("非管理员，请@段或戴进行设置修改")
            ]))

    if message.asDisplay().startswith("setone") and g.stage_get() < 2:
        if member.id == 2803309546 or member.id == 471608262:
            s = message.asDisplay().split(" ")
            g.set_setting_1(s)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(g.print_setting())
            ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id), Plain("非管理员，请@段或戴进行设置修改")
            ]))

    if message.asDisplay().startswith("setrule") and g.stage_get() < 2:
        if member.id == 2803309546 or member.id == 471608262:
            s = message.asDisplay().split(" ")
            g.set_rule(int(s[1]), int(s[2]))
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(g.get_rule()[0])
            ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id), Plain("非管理员，请@段或戴进行设置修改")
            ]))

    if message.asDisplay().startswith("reset"):
        if member.id == 2803309546 or member.id == 471608262:
            g.reset()
            role.reset_num()
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("reset success")
            ]))

    if message.asDisplay().startswith("setpolice"):
        if member.id == 2803309546 or member.id == 471608262:
            g.setpolice(int(message.asDisplay().split(" "))-1)

    # 狼人杀准备部分
    if message.asDisplay().startswith("狼人杀") and g.stage_get() == 1:
        # print(g.stage_get())
        await app.sendGroupMessage(group, MessageChain.create([
            Plain("请参赛者私发\"参加\"给bot")
        ]))
        g.stage_add()
        # print("lrs")
        # print(g.stage_get())  # 值为2

    # 狼人杀开始
    if message.asDisplay().startswith("开始"):
        if g.stage_get() < 3:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(g.print_setting() + "\n目前还缺" + str(g.full_all()) + "人")
            ]))
        elif g.stage_get() > 3:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("游戏已经开始了")
            ]))
        else:
            # 身份分配
            g.identity_random()
            users = g.get_all()
            real_id = g.get_set_value()
            # 给每个人发身份
            for i in range(0, len(users)):
                send_friend = users[i].get_friend()
                send_id = users[i].get_identity()
                # print(send_id)
                await app.sendFriendMessage(send_friend, MessageChain.create([
                    Plain("你的身份为" + real_id[send_id])
                ]))
            # g.identity_show()
            g.stage_add()
            # 值为4
            # 下一阶段判断是否有丘比特
            cupid = g.judge_by_identity(6)
            if cupid[0] != -1:  # 有丘比特
                await app.sendFriendMessage(cupid[1].get_friend(), MessageChain.create([
                    Plain("以\"连线 a b\"的格式发送编号")
                ]))
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("丘比特请选择要连线的两个人的编号")
                ]))
                await inc.wait(FriendMessageInterrupt(
                    cupid[1].get_friend(),
                    custom_judgement=lambda x: x.messageChain.asDisplay().startswith("连线")
                ), 100)
                g.stage_add()
            else:
                g.stage_add()
            # 阵营分配
            # print(g.stage_get())
            # print("gok")
            # 值应该为5了
            # 正营分配
            for i in range(0, len(users)):
                # print(users[i].get_union())
                if users[i].get_union() == -1:
                    identity = users[i].get_identity()
                    if identity < 2:
                        users[i].set_union(0)
                        g.add_list(1, users[i].get_no(), users[i])
                        # g.add_list(0, users[i].get_no(), users[i])
                    if identity > 1:
                        users[i].set_union(1)
                        # g.add_list(2, users[i].get_no(), users[i])
                        # g.add_list(0, users[i].get_no(), users[i])
            # print("gok\n")
            g.stage_add()

            g.init_if_alive()

            # 6
            # 第一晚
            await one_night(message, app, group, member)
            # 上警##############
            if g.get_rule()[0] == 1:
                # 参加上警
                g.init_police()
                print(g.stage_get())
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("请想要当警长的私发bot\"上警\"\n在群中发送\"警长\"以查看并开始投票")
                ]))
                # g.stage_add()
                await inc.wait(GroupMessageInterrupt(
                    group, member,
                    custom_judgement=lambda x: x.messageChain.asDisplay().startswith("警长")
                ))
                print("警长执行结束")
                print(g.stage_get())
                # stage=12
                # 投票
            else:
                g.stage_add()
                g.stage_add()

            await result(app, group)

    if message.asDisplay().startswith("投票") and g.stage_get() == 13:

        # print("vote")
        stat = 1
        g.init_vote()
        g.init_vote_every_one()
        users = g.get_all()
        for i in range(0, len(users)):
            if users[i].get_status() == 1:
                await app.sendFriendMessage(users[i].get_friend(), MessageChain.create([
                    Plain("请选择要投的人，\"投票 编号\"")
                ]))
                print(g.stage_get())
                await inc.wait(FriendMessageInterrupt(
                    users[i].get_friend(),
                    custom_judgement=lambda x: x.messageChain.asDisplay().startswith("投票 ")
                ), 100)
        print(g.get_vote_result())
        if len(g.get_vote_result()) == 1 and g.get_vote_result()[0] != -1:
            dead = g.get_one_bynum(g.get_vote_result()[0])
            dead.set_status(-2)
            g.add_list(4, dead.get_no, dead)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("投票结果为" + str(g.get_vote_result()[0]))
            ]))
        elif len(g.get_vote_result()) > 1:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("出现平票")
            ]))

            stat = 0
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(g.get_vote_info())
        ]))
        g.reset_vote_r()
        if stat == 0 and g.get("vote") == 0:
            g.set("vote", 1)

        else:
            g.set("vote", 0)
            g.stage_add()
            print(g.get_vote_result())
            # 14
            g.init_one_night_dead()
            await die()
            stri = ""
            res = g.get_one_night_dead()
            for i in range(0, len(res)):
                if res[i] == 1:
                    stri += str(i + 1) + "号死亡，有遗言\n"
                elif res[i] == 2:
                    stri += str(i + 1) + "号死亡，无遗言\n"
            if stri != "":
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(stri)
                ]))
            else:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("无人死亡")
                ]))

            await win()
            if g.get("win") == 0:
                g.stage_set(int(6))
                await one_night(message, app, group, member)
                await result(app, group)

    # temp
    if message.asDisplay().startswith("show"):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(g.union_show())
        ]))

        # 记得加stage判断

    # 警长
    if message.asDisplay().startswith("警长") and g.stage_get() == 10:

        # print("vote")
        stat = 1

        users = g.get_all()
        g.stage_add()
        p = g.get_police()
        string = "警长候选\n"
        for i in range(0, len(users)):
            if p[i] == 1:
                string += str(p[i] + 1) + "号\n"

        await app.sendGroupMessage(group, MessageChain.create([
            Plain(string)
        ]))
        for i in range(0, len(users)):
            await app.sendFriendMessage(users[i].get_friend(), MessageChain.create([
                Plain("请选择要投的人，\"投票 编号\"")
            ]))
            print(g.stage_get())
            await inc.wait(FriendMessageInterrupt(
                users[i].get_friend(),
                custom_judgement=lambda x: x.messageChain.asDisplay().startswith("投票 ")
            ), 100)
            print("okk")
        print(g.get_police_result())
        if len(g.get_police_result()) == 1 and g.get_police_result()[0] != -1:
            police = g.get_one_bynum(g.get_vote_result()[0])
            police.set_police()

            await app.sendGroupMessage(group, MessageChain.create([
                Plain("警长为" + str(g.get_police_result()[0]))
            ]))
        elif len(g.get_vote_result()) > 1:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("出现平票")
            ]))

            stat = 0
            # print(g.get_police_info())
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(g.get_police_info())
        ]))
        g.reset_police()
        if stat == 0 and g.get("vote") == 0:
            g.set("vote", 1)

        else:
            g.set("vote", 0)
            g.stage_add()
            print(g.get_police_result())


async def one_night(
        message: MessageChain,
        app: GraiaMiraiApplication,
        group: Group, member: Member,
):
    # 全局变量存储
    g = gol()
    users = g.get_all()
    g.init_vote()
    # print("进入方法，没进if\n")
    # wolf
    if g.stage_get() == 6:
        # print("if")
        await app.sendGroupMessage(group, MessageChain.create([
            Plain("天黑请闭眼，狼人请睁眼杀人")
        ]))
        wolf = g.get_list(1)
        # print("狼")
        # print(len(wolf))
        if len(wolf) != 0:
            g.init_vote_every_one()
            for key, values in g.get_list(1).items():
                if values.get_identity() < 2 and values.get_status() == 1:
                    await app.sendFriendMessage(values.get_friend(), MessageChain.create([
                        Plain("请选择要杀的人，\"杀人 编号\"")
                    ]))
                    await inc.wait(FriendMessageInterrupt(
                        values.get_friend(),
                        custom_judgement=lambda x: x.messageChain.asDisplay().startswith("杀人 ")
                    ), 100)
            if len(g.get_vote_result()) == 1 and g.get_vote_result()[0] != -1:
                dead = g.get_one_bynum(g.get_vote_result()[0])
                dead.set_status(-1)
                g.add_list(4, dead.get_no(), dead)
                for key, values in g.get_list(1).items():
                    if values.get_identity() < 2 and values.get_status() == 1:
                        await app.sendFriendMessage(values.get_friend(), MessageChain.create([
                            Plain("投票结果为" + str(g.get_vote_result()[0]))
                        ]))
            elif len(g.get_vote_result()) > 1:
                for key, values in g.get_list(1).items():
                    if values.get_identity() < 2 and values.get_status() == 1:
                        await app.sendFriendMessage(values.get_friend(), MessageChain.create([
                            Plain("出现平票，无人死亡")
                        ]))

        g.stage_add()
        # print(g.get_vote_result()[0])
        # 7
        # 预言家
    # yuyanjia
    if g.stage_get() == 7:
        if g.judge_if_have(3) == 1:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("预言家请选择要查验的对象")
            ]))
        prophet = g.judge_by_identity(3)
        if prophet[0] != -1:
            await app.sendFriendMessage(prophet[1].get_friend(), MessageChain.create([
                Plain("以\"查验 a\"的格式发送编号")
            ]))

            await inc.wait(FriendMessageInterrupt(
                prophet[1].get_friend(),
                custom_judgement=lambda x: x.messageChain.asDisplay().startswith("查验 ")
            ), 100)
            g.stage_add()
        else:
            g.stage_add()
        # 8
    # nvwu
    if g.stage_get() == 8:
        if g.judge_if_have(4) == 1:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("女巫请做出选择")
            ]))
        witch = g.judge_by_identity(4)
        st = ""
        if witch[0] != -1:
            if len(g.get_list(4).items()) != 0:
                st = str(list(g.get_list(4).items())[0][1].get_no())

            await app.sendFriendMessage(witch[1].get_friend(), MessageChain.create([
                Plain("今晚狼杀的是" + st + "要救吗？\n以\"救 是/否\"回答")
            ]))

            await inc.wait(FriendMessageInterrupt(
                witch[1].get_friend(),
                custom_judgement=lambda x: x.messageChain.asDisplay().startswith("救 ")
            ), 100)
            g.stage_add()
            # 9
            await app.sendFriendMessage(witch[1].get_friend(), MessageChain.create([
                Plain("要毒吗？\n以\"毒 编号\"或\"毒 否\"回答")
            ]))
            await inc.wait(FriendMessageInterrupt(
                witch[1].get_friend(),
                custom_judgement=lambda x: x.messageChain.asDisplay().startswith("毒 ")
            ), 100)
            g.stage_add()
            # 10
        else:
            g.stage_add()
            g.stage_add()


async def result(
        app: GraiaMiraiApplication,
        group: Group
):
    print("result")
    g = gol()
    g.init_one_night_dead()
    await die()
    stri = ""
    res = g.get_one_night_dead()
    for i in range(0, len(res)):
        if res[i] == 1:
            stri += str(i + 1) + "号死亡，有遗言\n"
        elif res[i] == 2:
            stri += str(i + 1) + "号死亡，无遗言\n"
    if stri != "":
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(stri)
        ]))
    else:
        await app.sendGroupMessage(group, MessageChain.create([
            Plain("无人死亡")
        ]))

    await win()
    g.stage_add()
    # 13


def vote(message: MessageChain, type: int):
    g = gol()
    # 狼
    if type == 0:
        st = message.asDisplay().split(" ")
        g.vote_one(int(st[1]))
    if type == 1:
        st = message.asDisplay().split(" ")
        g.vote_one(int(st[1]))


async def die():
    stat = 0
    g = gol()

    print("die556")
    print(g.get_one_night_dead())
    # grou = g.get("group")
    dead = g.get_list(4)
    # st = " "
    link = 0
    # for key, values in dead.items():
    #   print(key)
    # print(values.get_identity())
    #  print(values.get_status())
    for key, values in dead.items():
        print(values.get_status())
        if values.get_status() == -2:
            g.die(values.get_identity())
            # st += str(values.get_no()) + "号死亡，有遗言\n"
            g.set_if_alive(values.get_no() - 1)
            g.set_one_night_dead(values.get_no() - 1, 1)
        #   print("no")
        #  print(st)
        if values.get_status() == 0 or values.get_status() == -1:
            # print("被毒杀")
            g.die(values.get_identity())
            # st += str(values.get_no()) + "号死亡，无遗言\n"
            g.set_if_alive(values.get_no() - 1)
            g.set_one_night_dead(values.get_no() - 1, 2)
        #  print("yes")
        # print(st)
        if values.get_link() != -1 and values.get_status() < 1:
            values.get_link().set_status(values.get_status())
            stat = 1
            link = values.get_link()

        if values.get_identity() == 5 and values.get_status() < 0:
            await app.sendFriendMessage(values.get_friend(), MessageChain.create([
                Plain("你被杀了\n请选择要杀的人，\"开枪 编号\"\n或放弃开枪，\"开枪 否\"")
            ]))
            await inc.wait(FriendMessageInterrupt(
                values.get_friend(),
                custom_judgement=lambda x: x.messageChain.asDisplay().startswith("开枪 ")
            ), 100)
    print("die596")
    print(g.get_one_night_dead())
    g.reset_dead()
    # print("final")
    # print(st)

    if stat == 1 and g.get("cupid") == 0:
        print("cupid/n")
        print(link.get_no())
        g.set("cupid", 1)
        g.add_list(4, link.get_no(), link)
        await die()

    else:
        g.set("cupid", 0)


async def win():
    g = gol()
    grou = g.get("group")
    users = g.get_all()
    team = [0, 0, 0]
    for i in range(0, len(users)):

        if users[i].get_status() == 1:
            team[int(users[i].get_union())] = 1

    if team[0] + team[1] + team[2] == 1:
        if team[0] == 1:
            await app.sendGroupMessage(grou, MessageChain.create([
                Plain("狼胜")
            ]))
        elif team[1] == 1:
            await app.sendGroupMessage(grou, MessageChain.create([
                Plain("人胜")
            ]))
        else:
            await app.sendGroupMessage(grou, MessageChain.create([
                Plain("丘比特胜")
            ]))
        g.set("win", 1)
    elif team[0] + team[1] + team[2] == 0:
        await app.sendGroupMessage(grou, MessageChain.create([
            Plain("平局")
        ]))
        g.set("win", 1)
    else:
        await app.sendGroupMessage(grou, MessageChain.create([
            Plain("游戏继续")
        ]))
        # print(g.stage_get())


app.launch_blocking()
