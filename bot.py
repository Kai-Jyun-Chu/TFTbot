import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.message_content = True


# slash
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

client = MyClient()

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    await client.tree.sync()  # register slash
    print("✅ Slash commands synced.")



@client.tree.command(name="ping", description="123")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("123")

def scrape_lp_diff():
    print("setting Chrome options")
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    print("⬇downloading chromedriver ")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("crawling")
    try:
        # 
        driver.get("https://www.metatft.com/player/tw/曲凱鈞不配贏-2486")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "PlayerRankLP"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        lp = int(soup.find("div", class_="PlayerRankLP").text.strip().replace("LP", "").strip())

        #
        driver.get("https://www.metatft.com/leaderboard/tw")
        tw_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='TW']"))
        )
        tw_tab.click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "PromotionCutoffValue"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        text = soup.find("span", class_="PromotionCutoffValue").text.strip()
        challenger_lp = int(text.replace("LP", "").strip())

        diff = challenger_lp - lp
        if diff <= 0:
            return f"Congrat! Chen ting yu is already a Challenger!\n Standing at {lp} rn, Challenger line: {challenger_lp} "
        else:
            return f"☠️Challenger need {diff} LP"

    finally:
        driver.quit()


@client.tree.command(name="challenger", description="challenger - Chen ting yu")
async def challenger(interaction: discord.Interaction):
    await interaction.response.defer()  #
    try:
        # 
        result_msg = await asyncio.to_thread(scrape_lp_diff)
        await interaction.followup.send(result_msg)
    except Exception as e:
        await interaction.followup.send(f"[DEBUG] err{e}")

client.run(TOKEN)
