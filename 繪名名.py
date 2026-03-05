import discord
from discord.ext import commands
import asyncio
import random
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== 完整話題 JSON (純文字、觸發詞更多) =====
topics = {
    "累": {"keywords":["累","疲倦","困","想睡","昏昏沉沉","打瞌睡","嗜睡","精神不濟","瞌睡","累死了","想休息","累壞了"],
            "lines":["去休息吧","別硬撐","快躺下","真的累了吧","別再拖了","該休息就休息","累成這樣還能說話嗎"]},
    "畫": {"keywords":["畫","繪","塗鴉","畫畫","創作","作畫","手繪","畫圖","畫稿","素描","繪畫","速寫"],
            "lines":["草稿快給我","想畫什麼呢","別拖延","動筆吧","快畫完啦","作品準備好了嗎","還不動手嗎","把畫畫完成"]},
    "開心": {"keywords":["開心","高興","愉快","快樂","興奮","欣喜","幸福","喜悅","樂呵","爽","快樂死了","心情好"],
            "lines":["看你開心我也高興","今天心情不錯吧","好心情呀","真好呢","這樣就滿意了嗎","愉快的一天吧","開心就好"]},
    "煩": {"keywords":["煩","生氣","焦躁","煩躁","抓狂","氣憤","不爽","煩死了","心煩","火大","憤怒","受夠了"],
            "lines":["煩什麼啊","別鬧了","說吧，我在聽","冷靜一點","真的那麼煩嗎","放鬆點","別讓情緒控制你","別吵了"]},
    "睡覺": {"keywords":["睡覺","想睡","打盹","熬夜","晚安","睡不著","瞌睡","上床","睡意","睡覺時間","打盹了","累得想睡"],
            "lines":["快去睡吧","別熬夜了","做個好夢","閉上眼睛吧","休息是必要的","趕快睡覺","晚安，好好休息","睡吧，不要再拖了"]},
    "遊戲": {"keywords":["遊戲","打遊戲","玩LOL","Minecraft","Switch","王者榮耀","電競","手遊","手游","玩遊戲","打LOL","遊戲時間","電玩","玩耍","線上遊戲"],
            "lines":["你又在打遊戲？","羨慕你還有時間玩","贏了沒？","小心別沉迷","今天玩了什麼遊戲","別光玩遊戲","還能專心嗎","遊戲打得怎麼樣"]},
    "作業": {"keywords":["作業","功課","考試","練習","學校","報告","作業拖延","練習題","課業","作業完成","作業時間","作業進度","做功課","寫作業"],
            "lines":["快做作業啊","拖延也沒用","努力點吧","不要再偷懶","作業做好了嗎","該交作業了吧","快寫作業","別再拖了"]},
    "朋友": {"keywords":["朋友","同學","同伴","好友","室友","社團","同事","伙伴","好友聚會","朋友們","同學聚會","社交"],
            "lines":["又去找朋友了？","別只顧著朋友","今天和誰玩？","小心別被捉弄","和朋友玩得開心嗎","不要忘了我","朋友那邊怎麼樣","該陪我聊聊了吧"]},
    "戀愛": {"keywords":["戀愛","喜歡","暗戀","情人","愛情","告白","曖昧","心動","愛慕","暗戀對象","戀情","喜歡的人","愛人"],
            "lines":["戀愛了？","又在想那個人吧","小心別太心急","甜蜜呢","感覺幸福嗎","戀愛怎麼樣","心裡是不是甜滋滋的","別光顧著戀愛"]},
    "動漫": {"keywords":["動漫","動畫","漫畫","ACG","cos","二次元","新番","漫畫本","番劇","漫畫集","動漫作品","二次元世界","動畫片"],
            "lines":["又在看動漫？","哪部新番？","推薦我也看看","快告訴我劇情","今天追番了嗎","劇情好看嗎","漫畫看完了嗎","動漫內容如何"]},
    "音樂": {"keywords":["音樂","歌","唱歌","聽歌","鋼琴","吉他","Vocaloid","鋼琴曲","BGM","旋律","音樂作品","歌曲","聽音樂","彈琴","演奏"],
            "lines":["又在聽歌？","什麼曲子？","跟我分享一下吧","想唱給我聽嗎","今天聽什麼歌？","音樂好聽嗎","演奏過了嗎","音樂讓你心情好嗎"]},
    "運動": {"keywords":["運動","跑步","健身","籃球","足球","游泳","打球","瑜伽","健身房","慢跑","運動時間","健身運動","運動活動","體育"],
            "lines":["運動好累吧","今天有運動嗎","別偷懶啊","累得還能說話嗎","做運動了嗎","今天鍛煉了嗎","運動還順利嗎","有沒有認真運動"]},
    "天氣": {"keywords":["天氣","雨","下雨","晴天","颱風","冷","熱","風","下雪","天氣狀況","天氣好","溫度","氣候"],
            "lines":["天氣不錯吧","記得帶傘","好熱啊","冷得想躲被窩","天氣變化大","注意天氣","天氣還可以","今天天氣如何"]},
    "默認": {"keywords":[],"lines":["講重點","有事？","嗯？","我在聽","慢慢說","說清楚點","你想表達什麼","說吧"]}
}

# ===== 好感度存檔 =====
favor_data = {}

def get_favor(user_id):
    return favor_data.get(user_id,0)

def change_favor(user_id,amount):
    favor_data[user_id] = favor_data.get(user_id,0)+amount

# ===== 時間段問候 =====
def get_time_period():
    hour = datetime.now().hour
    if 5 <= hour < 12: return "morning"
    elif 12 <= hour < 18: return "afternoon"
    elif 18 <= hour < 23: return "evening"
    else: return "night"

def greeting_by_time():
    period = get_time_period()
    if period=="morning": return "早安"
    elif period == "afternoon":
        return "午安"
    elif period == "evening":
        return "晚安"
    else:
        return "深夜了，要注意休息"


def random_suffix(line):
    suffixes = ["", "吧", "啊", "呢", "…"]
    return line + random.choice(suffixes)


def hidden_line(lines):
    if random.random() < 0.1:
        lines += ["其實我剛剛在等你", "別突然消失", "今天想多聊一點"]
    return lines


# ===== 訊息事件 =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    msg = message.content.lower()
    favor = get_favor(user_id)
    in_session = False

    # 啟動對話
    if not hasattr(bot, "active_sessions"):
        bot.active_sessions = {}
    if user_id in bot.active_sessions:
        if datetime.now() < bot.active_sessions[user_id]:
            in_session = True
        else:
            del bot.active_sessions[user_id]

    if "繪名" in msg:
        bot.active_sessions[user_id] = datetime.now() + timedelta(seconds=30)
        if not in_session:
            greet = greeting_by_time()
            await message.channel.send(f"{greet}，你叫我啦？")
        in_session = True

    if not in_session:
        await bot.process_commands(message)
        return

    if "好感" in msg:
        await message.channel.send(f"目前好感度：{get_favor(user_id)}")
        return

    # 話題匹配
    matched=[]
    for topic,data in topics.items():
        if any(k in msg for k in data.get("keywords",[])):
            matched.append(topic)
    topic=random.choice(matched) if matched else "默認"

    # 好感變化
    if topic not in ["煩","默認"]:
        change_favor(user_id,1)
    elif topic=="煩":
        change_favor(user_id,-1)
    else:
        change_favor(user_id,0)

    # 上下文記憶
    if not hasattr(bot,"user_memory"):
        bot.user_memory={}
    mem=bot.user_memory.get(user_id,[])
    if len(mem)>=5: mem.pop(0)
    mem.append(msg)
    bot.user_memory[user_id]=mem

    # 生成回覆
    lines=topics.get(topic,topics["默認"])["lines"]
    lines=hidden_line(lines)
    response=random_suffix(random.choice(lines))

    delay=min(1.0+len(response)*0.05,5.0)
    await asyncio.sleep(delay)
    await message.channel.send(response)
    await bot.process_commands(message)

# ===== 啟動 BOT =====
bot.run("DISCORD_BOT_TOKEN")
