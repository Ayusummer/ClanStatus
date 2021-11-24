import os
import sqlite3
from nonebot import get_bot

import hoshino
from hoshino import Service
from hoshino.typing import CQEvent

sv = Service('会战状态', enable_on_default=True, help_='会战状态')

# 本地 yobot 数据库的路径
path_db = "/home/ubuntu/Karyl_1/yobot/src/client/yobot_data/yobotdata.db"


@sv.on_command('状态')
async def status(session):
    # 获取所在群号
    gid = session.ctx['group_id']
    # 连接 yoboqdata.db
    conn = sqlite3.connect(path_db)
    # 创建 cursor
    cur = conn.cursor()

    # sql: find last challenge_pcrdate by cid from clan_challenge
    sql_find_last_date = "SELECT challenge_pcrdate FROM clan_challenge \
                            ORDER BY cid DESC LIMIT 1"

    # select last row's challenge_pcrdate 获取当天的 pcrdate
    curr_date: int = cur.execute(sql_find_last_date).fetchone()[0]

    # 获取当天的所有会战数据的 qqid, boss_health_ramain, is_continue 打组
    sql_get_lastDate_data = "SELECT qqid, boss_health_ramain, is_continue FROM clan_challenge \
                            WHERE challenge_pcrdate = {0} and gid = {1} \
                                ORDER BY qqid".format(curr_date, gid)
    data_lastDate = cur.execute(sql_get_lastDate_data).fetchall()

    # 将会战信息按照 qqid 分组, 每组表示一个成员当天的出刀情况
    data_simple_data_split = []
    for i in range(len(data_lastDate)):
        if i == 0:
            data_simple_data_split.append([data_lastDate[i]])
        else:
            if data_lastDate[i][0] == data_lastDate[i-1][0]:
                data_simple_data_split[-1].append(data_lastDate[i])
            else:
                data_simple_data_split.append([data_lastDate[i]])

    """ 遍历每组出刀情况获取总的出刀情况
        attack_full: 已出的完整刀的数量
        attack_half: 剩余的补偿刀的数量
        attack_half_lst: 手中还有补偿刀的成员的 qqid
    """
    attacked_full, attacked_half, attacked_half_lst = 0, 0, []
    for i in data_simple_data_split:
        full, half = 0, 0
        for j in i:
            if j[1] == 0:
                half = 1
            full += 1
            if j[2] == 1:
                half = 0
                full -= 1
        if half == 1:
            full -= 1
            attacked_half_lst.append(i[0][0])
        attacked_full += full
        attacked_half += half

    # 查 user 表获取成员昵称
    sql_find_nickname = "SELECT qqid, nickname FROM user WHERE qqid = ?"
    nickname_lst = []
    for i in attacked_half_lst:
        nickname_lst.append(cur.execute(sql_find_nickname, (i,)).fetchone()[1])

    # 关闭 cursor
    cur.close()
    # 关闭数据库连接
    conn.close()

    msg = "手中还有补偿刀的成员为:{0}".format(nickname_lst)
    await session.send(msg)
