from config import vk_api
import sqlite3 as sq
import aiohttp
import time


async def check_user(message_id):
    results = []

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.vk.com/method/users.get') as response:
            sex = [["была в сети", "был в сети"], ["в сети", "в сети"]]
            device = ["с мобильного", "с iPhone", "с iPad", "с Android", "с Windows Phone", "с Windows 10", "с ПК",
                      "с VK Mobile"]

            response = await response.json()
            with sq.connect('database.db') as con:
                cur = con.cursor()
                cur.execute('SELECT ids FROM vk_id WHERE user_id = ?', (message_id,))
                rows = cur.fetchall()
                idss = [row[0] for row in rows]

            user_ids = ",".join(str(e) for e in idss)
            get_link = f"https://api.vk.com/method/users.get?user_ids={user_ids}&fields=sex,online,last_seen&access_token={vk_api}&v=5.85&lang=ru"

            async with session.get(get_link) as response:
                json = await response.json()
                user_online = 0

                for userinfo in json["response"]:
                    try:
                        userstat = userinfo["last_seen"]
                        user_id = userinfo["id"]
                    except:
                        continue
                    ms_time = time.gmtime(int(userstat["time"]) + 10800)

                    if userinfo['online'] == 1:
                        online = f"✅<code>id{user_id}</code> - {device[int(userstat['platform']) - 1]}"
                        user_online += 1
                        results.append(online)
                        with sq.connect('database.db') as con:
                            cur = con.cursor()
                            cur.execute('UPDATE vk_id SET off = ? WHERE ids = ?', (0, user_id))
                            con.commit()
                    else:
                        offline = f"❌<code>id{user_id}</code> - {device[int(userstat['platform']) - 1]}, {time.strftime('%d %b %Y %H:%M', ms_time)}"
                        with sq.connect('database.db') as con:
                            cur = con.cursor()
                            cur.execute('UPDATE vk_id SET off = ? WHERE ids = ?', (1, user_id))
                            con.commit()
                        results.append(offline)

    return results
