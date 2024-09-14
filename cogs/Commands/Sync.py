"""
Copyright (c) 2024 메보
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import discord
from discord import app_commands
from discord.ext import commands
import pymysql
import requests
import datetime

def get_db_connection():
    connection = pymysql.connect(
        host="svc.sel5.cloudtype.app",
        user="root",
        port=32103,
        password="pass",
        db='ikea_intranet',
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
AdminList = []

class NotAdmin(Exception):    
    def __init__(self):
        super().__init__('이 명령에 대한 권한이 부족합니다.')
        
    async def send_error_message(self, interaction):
        embed = discord.Embed(
            title="커맨드 오류",
            color=discord.Color.red()
        )
        embed.add_field(name="오류 분류", value="권한 오류", inline=False)
        embed.add_field(name="오류 내용", value="해당 명령에 대한 권한이 부족합니다", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        

class Sync(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('이케아 동기화 시스템이 로드 되었습니다.')
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx) -> None:
        try:
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"{len(fmt)}개의 명령어가 동기화 되었습니다.")
        except Exception as e:
            print(f"{e}")
        return
async def setup(bot):
    await bot.add_cog(Sync(bot),
                        guilds=[discord.Object(id=1184482371047800892)])
