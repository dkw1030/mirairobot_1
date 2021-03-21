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
async def friend_message_listener(app: GraiaMiraiApplication, friend: Friend):
    g = gol()
    g.set("friend", friend)

    await app.sendFriendMessage(g.get("friend"), MessageChain.create([
        Plain(g.get("friend").id)
    ]))


@bcc.receiver("GroupMessage")
async def group_message_handler(
        message: MessageChain,
        app: GraiaMiraiApplication,
        group: Group, member: Member,
):
    g = gol()
    if message.asDisplay().startswith("1"):
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id), Plain("发送 2 以继续运行")
        ]))
        await inc.wait(GroupMessageInterrupt(
            group, member,
            custom_judgement=lambda x: x.messageChain.asDisplay().startswith("2")
        ))
        await app.sendGroupMessage(group, MessageChain.create([
            Plain("接3")
        ]))
        s = g.get("friend")
        await inc.wait(FriendMessageInterrupt(
            s,
            custom_judgement=lambda x: x.messageChain.asDisplay().startswith("3")
        ))

        await app.sendGroupMessage(group, MessageChain.create([
            Plain(f"执行完毕.{s.id}")
        ]))


app.launch_blocking()
