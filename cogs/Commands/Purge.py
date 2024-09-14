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

class purge(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('이케아 메세지관리 시스템이 로드 되었습니다.')
        
    @app_commands.command(name="청소", description="메세지를 청소합니다 ( 서버 오너만 가능 )")
    async def purge(self, interaction: discord.Interaction, amount: int):
        AdminList = [interaction.guild.owner_id, 381620167160889364]
        
        try:
            if interaction.user.id in AdminList:
                try:
                    if amount <= 0:
                        await interaction.response.send_message("1 이상의 값을 입력하세요.", ephemeral=True)
                        return

                    await interaction.response.defer(ephemeral=True)
                    
                    def check(msg):
                        return msg.id != interaction.id
                    
                    deleted = await interaction.channel.purge(limit=amount, check=check)
                    channel = self.bot.get_channel(1259715536967958659)
                    
                    embed = discord.Embed(
                        title="삭제 완료",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="삭제 갯수", value=f"{len(deleted)}", inline=False)
                    embed.timestamp = datetime.datetime.now()
                    embed.set_footer(text="정상적으로 처리되었습니다 Made By Mebo")
                    
                    e = discord.Embed(
                        title="메세지 삭제 로그",
                        color=discord.Color.green()
                    )
                    e.add_field(name="삭제 갯수", value=f"{len(deleted)}", inline=False)
                    e.add_field(name="담당자", value=f"{interaction.user.nick}({interaction.user.id})", inline=False)
                    e.timestamp = datetime.datetime.now()
                    e.set_footer(text="정상적으로 처리되었습니다 Made By Mebo")
                    
                    await interaction.followup.send(embed=embed)
                    await channel.send(embed=e)
                except Exception as e:
                    print(e)
            else:
                raise NotAdmin()
        except NotAdmin as e:
            await e.send_error_message(interaction)

            
async def setup(bot):
    await bot.add_cog(purge(bot),
                        guilds=[discord.Object(id=1184482371047800892)])
