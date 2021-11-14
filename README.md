# ClanStatus
Hoshino 2 模块, 读取 yobot 的 sqlite3 数据库反馈当前会战状态(已出刀数,剩余完整刀和补偿刀数. 手上还有补偿的成员昵称)

---
## 部署说明

- 使用 `cd` 命令转到 `hoshino` 的 `modules` 目录

- `clone` 此 `repo`  
  ```bash
    git clone https://github.com/Ayusummer/ClanStatus.git
  ```
- 打开 `clan_status.py`, 修改 line11 yobot 数据库的路径
- 打开 `__bot__.py` 在 `MODULES_ON` 中添加 `'ClanStatus'`
- 重启 `hoshino`

---
## 使用说明
- 在群聊中发送 `状态` 即可获得反馈   
  ![image](https://user-images.githubusercontent.com/59549826/141664088-d42f01a0-7705-42aa-ba64-ad212e552d15.png)

---
## 逻辑说明
> 逻辑冗余很多, sql 不熟练🥲
- 读 `yobotdata.db` 的 `clan_challenge` 表获取最后一个 `pcrdate` 中所有数据的 `qqid, boss_health_ramain, is_continue` 送 `data_lastDate`
- 将 `data_lastDate` 按照 `qqid` 分组生成列表 `data_simple_data_split`, 每组表示一个成员的当日出刀数据
- 遍历 `data_simple_data_split`
  - 每组列表根据 `boss_health_remain` 判断是否手上还有补偿刀并计算出该成员已出的完整刀;   
    若手中有补偿刀则将此 qqid 写入 `attacked_half_lst(手中还有补偿刀的 qqid 列表)`
  - 遍历完所有组得出总的整刀数目和补偿刀数目
- 遍历 `attacked_half_lst` 查 `user` 表得出 `nickname`
- 反馈补偿刀情况

---
## CHANGELOG
- v1.0.0  
  - 经群友提醒发现 yobot 今年的 release 中已经有出刀数了, 那索性只留个补偿刀名单就行了(
    > 才发现个人自用的 yobot 已经落后将近一年的版本了(
  - 删除多余的完整刀和补偿刀数目的功能, 只保留一个补偿刀名单的功能
- v0.0.0
  - 初版, 包含查完整刀, 补偿刀数目以及手中还有补偿刀的成员名单的功能

