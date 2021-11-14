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

    # 获取当天的所有会战数据
    sql_get_lastDate_data = "SELECT * FROM clan_challenge \
                            WHERE challenge_pcrdate = {0} and gid = {1}".format(curr_date, gid)
    data_lastDate = cur.execute(sql_get_lastDate_data).fetchall()

    """ 创建当天的会战信息表
        这里也可以不建表, 建表主要是为了之后可能存在的功能扩展(大概
        不建表的话直接转到 line 67 提取 qqid, boss_health_remain 就行了
    """
    sql_create_table_lastDate = """CREATE TABLE IF NOT EXISTS table_lastDate 
                                (  cid INTEGER PRIMARY KEY,
                                    bid INTEGER,
                                    gid INTEGER,
                                    qqid INTEGER,
                                    challenge_pcrdate INTEGER,
                                    challenge_pcrtime INTEGER,
                                    boss_cycle INTEGER,
                                    boss_num    INTEGER,
                                    boss_health_remain INTEGER,
                                    challenge_damage INTEGER,
                                    is_continue INTEGER,
                                    message TEXT,
                                    behalf INTEGER );
                            """
    cur.execute(sql_create_table_lastDate)

    # rewrite table_lastDate with data_lastDate 将当天的会战信息写入表
    sql_rewrite_table_lastDate = "INSERT INTO table_lastDate \
                                (cid, bid, gid, qqid, challenge_pcrdate, challenge_pcrtime, boss_cycle, boss_num, boss_health_remain, challenge_damage, is_continue, message, behalf) \
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cur.executemany(sql_rewrite_table_lastDate, data_lastDate)

    # get all date from table_lastDate  获取当天所有的会战信息
    sql_get_all_lastDate = "SELECT * FROM table_lastDate"
    data_all_lastDate = cur.execute(sql_get_all_lastDate).fetchall()

    # get [cid, qqid, boss_health_remain, is_continue] from table_lastDate oder by qqid 
    sql_get_simple_data = "SELECT cid, qqid, boss_health_remain, is_continue FROM table_lastDate \
                                    ORDER BY qqid"
    data_simple_data = cur.execute(sql_get_simple_data).fetchall()

    # split data_simple_data by qqid 将会战信息按照 qqid 分组, 每组表示一个成员当天的出刀情况
    data_simple_data_split = []
    for i in range(len(data_simple_data)):
        if i == 0:
            data_simple_data_split.append([data_simple_data[i]])
        else:
            if data_simple_data[i][1] == data_simple_data[i-1][1]:
                data_simple_data_split[-1].append(data_simple_data[i])
            else:
                data_simple_data_split.append([data_simple_data[i]])

    """ 遍历每组出刀情况获取总的出刀情况
        attack_full: 已出的完整刀的数量
        attack_half: 剩余的补偿刀的数量
        attack_half_lst: 手中还有补偿刀的成员的 qqid
    """
    attacked_full, attacked_half, attacked_half_lst = 0, 0, []
    for i in data_simple_data_split:
        full, half = 0, 0
        for j in i:
            if j[2] == 0:
                half = 1
            full += 1
            if j[3] == 1:
                half = 0
                full -= 1
        if half == 1:
            full -= 1
            attacked_half_lst.append(i[0][1])
        attacked_full += full
        attacked_half += half

    # find nickname by attacked_half_lst in user table  通过 attacked_half_lst 查 user 表获取成员昵称
    sql_find_nickname = "SELECT qqid, nickname FROM user WHERE qqid = ?"
    nickname_lst = []
    for i in attacked_half_lst:
        nickname_lst.append(cur.execute(sql_find_nickname, (i,)).fetchone()[1])

    msg= "当前已出{0}刀完整刀, 还剩{1}刀完整刀和{2}刀补偿刀 \n \
            手中还有补偿刀的成员为:{3}".format(attacked_full, 90-attacked_half-attacked_full, attacked_half, nickname_lst)
    await session.send(msg)