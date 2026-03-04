import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "favor_data.json"
active_sessions = {}  # 使用者對話狀態（30秒內）

# ===== 讀寫好感度資料 =====
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

def get_favor(user_id):
    data = load_data()
    return data.get(str(user_id), 0)

def change_favor(user_id, amount):
    data = load_data()
    uid = str(user_id)
    data[uid] = data.get(uid, 0) + amount
    save_data(data)

# ===== 時間段 =====
def get_time_period():
    hour = datetime.now().hour
    if 0 <= hour < 5:
        return "late_night"
    elif 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    else:
        return "night"

# ===== 語氣判定 =====
def get_tone(favor):
    if favor <= -5:
        return "cold"
    elif favor < 10:
        return "normal"
    else:
        return "warm"

# ===== 給台詞加隨機表情/尾巴 =====
def random_suffix(line):
    suffixes = ["😏", "…", "！", "🙄", "…唔", ""]
    return line + random.choice(suffixes)

# ===== 隱藏彩蛋 =====
def hidden_line(lines):
    if random.random() < 0.1:  # 10% 機率
        lines += [
            "……其實我剛剛在等你。",
            "別突然消失。",
            "今天想多聊一點。"
        ]
    return lines

# ===== 處理訊息 =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    msg = message.content
    now = datetime.now()
    favor = get_favor(user_id)
    tone = get_tone(favor)
    period = get_time_period()

    # ===== 對話模式判斷 =====
    in_session = False
    if user_id in active_sessions:
        if now < active_sessions[user_id]:
            in_session = True
        else:
            # 對話結束提示
            await message.channel.send("不聊了？")
            del active_sessions[user_id]

    if "繪名" in msg:
        active_sessions[user_id] = now + timedelta(seconds=30)
        if not in_session:
            await message.channel.send(random.choice([
                "嗯？", "啊，你來了。", "又找我？"
            ]))
        in_session = True

    if not in_session:
        await bot.process_commands(message)
        return

    # ===== 好感查詢 =====
    if "好感" in msg:
        await message.channel.send(f"目前好感度：{favor}")
        return

    # ===== 關鍵字互動 =====
    response = None

    # 累
    if "累" in msg:
        change_favor(user_id, 1)
        lines = []
        if tone == "cold":
            lines = ["自找的。", "誰叫你不睡。"]
        elif tone == "normal":
            lines = ["去休息一下。", "水喝了沒？", "別硬撐。"]
        else:
            lines = ["辛苦了。", "去躺一下，我還在。", "要不要休息？"]

        if period == "late_night":
            lines += ["這麼晚還撐？", "熬夜啊…"]

        response = random_suffix(random.choice(hidden_line(lines)))

    # 畫
    elif "畫" in msg:
        change_favor(user_id, 2)
        lines = []
        if tone == "cold":
            lines = ["別裝認真。", "三分鐘熱度。", "動筆吧。"]
        elif tone == "normal":
            lines = ["草稿給我看。", "別拖。", "今天要畫啥？"]
        else:
            lines = ["想畫什麼？", "我陪你想靈感。", "慢慢來也沒關係。"]

        response = random_suffix(random.choice(hidden_line(lines)))

    # 提到別人（吃醋）
    elif "別人" in msg or "他" in msg:
        if favor >= 5 and random.random() < 0.4:
            response = random_suffix(random.choice([
                "你最近很常提別人。",
                "那你去找他啊。",
                "……哦。"
            ]))
        else:
            change_favor(user_id, -1)
            response = random_suffix(random.choice(["嗯。", "隨你。"]))

    # 安安
    elif "安" in msg:
        change_favor(user_id, 1)
        lines = []
        if tone == "cold":
            lines = ["安什麼。", "嗯。"]
        elif tone == "normal":
            lines = ["安。", "今天怎樣？", "你今天還好嗎？"]
        else:
            lines = ["你來了。", "嗯，安安。", "今天心情還行嗎？"]

        response = random_suffix(random.choice(hidden_line(lines)))

    # 沒有關鍵字
    else:
        change_favor(user_id, -1)
        lines = []
        if tone == "cold":
            lines = ["講重點。", "有事？", "快說。"]
        elif tone == "normal":
            lines = ["嗯？", "說吧。", "你想幹嘛？"]
        else:
            lines = ["我在聽。", "慢慢說。", "嗯？"]

        response = random_suffix(random.choice(hidden_line(lines)))

    if response:
        await message.channel.send(response)

    await bot.process_commands(message)

# ===== 啟動 BOT =====
bot.run("DISCORD_BOT_TOKEN")