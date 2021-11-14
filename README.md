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
  <!--   ![20211114092554](http:cdn.ayusummer233.top/img/20211114092554.png) -->
  ![image](https://user-images.githubusercontent.com/59549826/141664088-d42f01a0-7705-42aa-ba64-ad212e552d15.png)
