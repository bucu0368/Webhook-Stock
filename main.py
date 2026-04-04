import discord
from discord import Webhook
import aiohttp
import asyncio
from datetime import datetime

# --- CẤU HÌNH ---
WEBHOOK_URL = 'https://discord.com/api/webhooks/1412898849193984175/TYwx-LZk7V0bku7-8jrEhnGFs1M2GP-KkGSgiuCj0AbWN6dUzeOHrQtv5S_KiV7XzTj7'
API_URL = "https://test-hub.kys.gay/api/stock"
LOGO_URL = "https://cdn.discordapp.com/avatars/1373611245206372444/f847c5205b749a3490607ad8a308d77f.png?size=1024"
SUPPORT_URL = "https://discord.gg/Zg2XkS5hq9"
BOT_NAME = "AvalonX • Live Stock Bot"
POLL_INTERVAL = 60  # giây

# --- MÀU SẮC WEBHOOK ---
# Bạn có thể chọn 0x000000 (Đen) hoặc 0x8800ff (Tím) hoặc bất kỳ màu nào
WEBHOOK_COLOR = 0x000000 

# --- BẢNG TRA CỨU EMOJI ---
FRUIT_EMOJIS = {
    "Spring": "<:spring:1321169507913437194>", "Spirit": "<:spirit:1321171299208532060>",
    "Spin": "<:spin:1321169504109203457>", "Spike": "<:spike:1321171000565432410>",
    "Tiger": "<:tiger:1445624043486052394>", "T-Rex": "<:trex:1321171300630401074>",
    "Venom": "<:venom:1321169511797358602>", "Yeti": "<:yeti:1321516411679408259>",
    "Spider": "<:spider:1321169500971728927>", "Sound": "<:sound:1321170999521317024>",
    "Smoke": "<:smoke:1321169497121620049>", "Shadow": "<:shadow:1321170730939060326>",
    "Sand": "<:sand:1321169493841547334>", "Rumble": "<:rumble:1321170729957462026>",
    "Rubber": "<:rubber:1321169490356080705>", "Rocket": "<:rocket:1321170617008914463>",
    "Quake": "<:quake:1321169486757363713>", "Portal": "<:portal:1321170473677226065>",
    "Phoenix": "<:phoenix:1321169484257558578>", "Pain": "<:pain:1321170472775192616>",
    "Mammoth": "<:mammoth:1321169480885211287>", "Magma": "<:magma:1321169746020012082>",
    "Love": "<:love:1321169476414210128>", "Light": "<:light:1321169744119730258>",
    "Kitsune": "<:kitsune:1321169743041921106>", "Ice": "<:ice:1321169469657190461>",
    "Gravity": "<:gravity:1321169741850873916>", "Ghost": "<:ghost:1321169466758926376>",
    "Gas": "<:gas:1321159135483658281>", "Flame": "<:flame:1321169740722602012>",
    "Falcon": "<:falcon:1321169462518354013>", "Dragon": "<:dragon:1321169738671325256>",
    "Dough": "<:dough:1321169459397791784>", "Diamond": "<:diamond:1321163280789536849>",
    "Dark": "<:dark:1321169457975918777>", "Creation": "<:creation:1445624076973379687>",
    "Control": "<:control:1321169456348528673>", "Buddha": "<:buddha:1321169455111208992>",
    "Bomb": "<:bomb:1321169454234734622>", "Blizzard": "<:blizzard:1321169453324570725>",
    "Blade": "<:blade:1321169452519133276>", "Barrier": "<:barrier:1321169451567022110>"
}
BELI_EMOJI = "<:money:1456628926276173845>"

def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def stock_signature(stock_list: list) -> frozenset:
    return frozenset(item.get('name', '') for item in stock_list)

def format_stock(stock_list: list) -> str:
    if not stock_list:
        return "Hiện tại không có stock."
    lines = []
    for item in stock_list:
        name = item.get('name', 'Unknown')
        price = f"{item.get('price_beli', 0):,}"
        emoji = FRUIT_EMOJIS.get(name, "🍎")
        lines.append(f"{emoji} **{name} • {BELI_EMOJI} `{price}`**")
    return "\n".join(lines)

async def send_webhook(
    session: aiohttp.ClientSession,
    json_data: dict,
    data: dict,
    timers: dict,
    mirage_reset: bool,
    normal_reset: bool,
    is_startup: bool = False
):
    all_items = data.get('mirage_stock', []) + data.get('normal_stock', [])
    top_fruit = max(all_items, key=lambda x: x.get('price_beli', 0), default=None)
    thumbnail_url = top_fruit.get('image_url', LOGO_URL) if top_fruit else LOGO_URL
    top_name = top_fruit.get('name', 'N/A') if top_fruit else 'N/A'
    top_price = f"{top_fruit.get('price_beli', 0):,}" if top_fruit else 'N/A'
    top_emoji = FRUIT_EMOJIS.get(top_name, "🍎")

    if is_startup:
        event_label = "🟢 Bot khởi động — Stock hiện tại"
    elif mirage_reset and normal_reset:
        event_label = "🔄 Cả 2 kho vừa **RESET**!"
    elif mirage_reset:
        event_label = "🏝️ **Mirage Island** vừa RESET!"
    else:
        event_label = "🛒 **Normal Shop** vừa RESET!"

    webhook = Webhook.from_url(WEBHOOK_URL, session=session)
    view = discord.ui.LayoutView()
    
    # Áp dụng màu từ cấu hình WEBHOOK_COLOR
    container = discord.ui.Container(accent_colour=discord.Colour(WEBHOOK_COLOR))

    # --- Header ---
    header_section = discord.ui.Section(
        discord.ui.TextDisplay(content=f"### 🍎 BLOXFRUIT LIVE STOCK"),
        discord.ui.TextDisplay(
            content=(
                f"{event_label}\n"
                f"Cập nhật từ hệ thống **{json_data.get('provider', 'BloxFruit')}**\n"
                f"-# 👑 Fruit đắt nhất: {top_emoji} **{top_name}** — {BELI_EMOJI} `{top_price}`"
            )
        ),
        accessory=discord.ui.Thumbnail(media=thumbnail_url)
    )
    container.add_item(header_section)
    container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

    # --- Stocks ---
    container.add_item(discord.ui.TextDisplay(content=f"### 🏝️ Mirage Island Stock\n{format_stock(data.get('mirage_stock', []))}"))
    container.add_item(discord.ui.Separator())
    container.add_item(discord.ui.TextDisplay(content=f"### 🛒 Normal Shop Stock\n{format_stock(data.get('normal_stock', []))}"))
    container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))

    # --- Timers ---
    reset_text = (
        f"### ⏰ Trình thời gian\n"
        f"⏳ Mirage Reset: `{timers.get('mirage_reset_in', 'N/A')}`\n"
        f"🛒 Normal Reset: `{timers.get('normal_reset_in', 'N/A')}`"
    )
    container.add_item(discord.ui.TextDisplay(content=reset_text))
    container.add_item(discord.ui.Separator())

    # --- Support ---
    support_button = discord.ui.Button(style=discord.ButtonStyle.link, label="💬 Support Server", url=SUPPORT_URL)
    container.add_item(discord.ui.ActionRow(support_button))
    container.add_item(discord.ui.Separator())
    container.add_item(discord.ui.TextDisplay(content=f"-# {BOT_NAME} • Tự động cập nhật"))

    view.add_item(container)

    await webhook.send(
        view=view,
        username=BOT_NAME,
        avatar_url=LOGO_URL
    )

async def fetch_stock(session: aiohttp.ClientSession):
    try:
        async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=15)) as response:
            if response.status == 200:
                json_data = await response.json()
                return json_data, json_data.get('data', {}), json_data.get('timers', {})
    except Exception as e:
        log(f"❌ Lỗi kết nối: {e}")
    return None

async def main():
    log(f"🚀 {BOT_NAME} khởi động — chạy 24/7 với màu 0x{WEBHOOK_COLOR:06x}")
    prev_mirage_sig, prev_normal_sig = None, None
    is_startup = True

    async with aiohttp.ClientSession() as session:
        while True:
            result = await fetch_stock(session)
            if result:
                json_data, data, timers = result
                cur_mirage_sig = stock_signature(data.get('mirage_stock', []))
                cur_normal_sig = stock_signature(data.get('normal_stock', []))

                if is_startup or cur_mirage_sig != prev_mirage_sig or cur_normal_sig != prev_normal_sig:
                    mirage_reset = not is_startup and cur_mirage_sig != prev_mirage_sig
                    normal_reset = not is_startup and cur_normal_sig != prev_normal_sig
                    try:
                        await send_webhook(session, json_data, data, timers, mirage_reset, normal_reset, is_startup)
                        log("✅ Đã cập nhật Webhook thành công.")
                    except Exception as e:
                        log(f"❌ Lỗi gửi webhook: {e}")

                prev_mirage_sig, prev_normal_sig = cur_mirage_sig, cur_normal_sig
                is_startup = False
            
            await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
