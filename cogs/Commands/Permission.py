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

class permission(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('이케아 권한관리 시스템이 로드 되었습니다.')

    @app_commands.command(name="권한", description="유저의 프로그램 권한을 제어합니다.")
    @app_commands.choices(choices=[
        app_commands.Choice(name="추가",value="add"),
        app_commands.Choice(name="제거",value="remove"),
    ],role=[
        app_commands.Choice(name="관리자",value="admin"),
        app_commands.Choice(name="DB관리자",value="DB_admin"),
        app_commands.Choice(name="감사팀",value="team_audit"),
        app_commands.Choice(name="인사팀",value="team_hr"),
        app_commands.Choice(name="교육팀",value="team_edu")
    ])
    async def permission(self,
                        interaction:discord.Interaction,
                        choices: app_commands.Choice[str],
                        role:app_commands.Choice[str],
                        personalnum: int):
        embed = discord.Embed(title="메보 이케아 권한관리 시스템",color=discord.Color.green())
        embed.timestamp=datetime.datetime.now()
        AdminList = [interaction.guild.owner_id,381620167160889364]
        try:
            if (choices.value == "add"):
                if (role.value == "admin"):
                    try:
                        if interaction.user.id in AdminList:
                            connection = get_db_connection()
                            with connection.cursor() as cursor:
                                query = "SELECT * FROM admin WHERE PersonalNum=%s"
                                cursor.execute(query, (personalnum,))
                                user = cursor.fetchone()
                                if(user):
                                    await interaction.response.send_message(
                                        embed = discord.Embed(title="커맨드 오류",
                                        description="이미 권한이 존재하는 사용자입니다.",
                                        color=discord.Color.red()),ephemeral=True
                                    )
                                    return
                            with connection.cursor() as cursor:
                                cursor.execute("INSERT INTO admin(PersonalNum) VALUES (%s)",(personalnum))
                                connection.commit()
                        else:
                            raise NotAdmin()
                    except NotAdmin as e:
                        await e.send_error_message(interaction)
                            
                if(role.value == "DB_admin"):
                    try:
                        if interaction.user.id in AdminList:
                            connection = get_db_connection()
                            with connection.cursor() as cursor:
                                query = "SELECT * FROM db_admin WHERE PersonalNum=%s"
                                cursor.execute(query, (personalnum,))
                                user = cursor.fetchone()
                                if(user):
                                    await interaction.response.send_message(
                                        embed = discord.Embed(title="커맨드 오류",
                                        description="이미 권한이 존재하는 사용자입니다.",
                                        color=discord.Color.red()),ephemeral=True
                                    )
                                    return
                            with connection.cursor() as cursor:
                                cursor.execute("INSERT INTO admin(PersonalNum) VALUES (%s)",(personalnum))
                                connection.commit()
                        else:
                            raise NotAdmin()
                    except NotAdmin as e:
                        await e.send_error_message(interaction)
            elif (choices.value == "remove"):
                embed.color=discord.Color.red()
                try:
                    if interaction.user.id in AdminList:
                        if(role.value == "admin"):
                            connection = get_db_connection()
                            with connection.cursor() as cursor:
                                cursor.execute(f"DELETE FROM admin WHERE PersonalNum ='{personalnum}'")
                                connection.commit()
                                    
                        elif(role.value == "DB_admin"):
                                connection = get_db_connection()
                                with connection.cursor() as cursor:
                                    cursor.execute(f"DELETE FROM db_admin WHERE PersonalNum = '{personalnum}'")
                    else:
                        raise NotAdmin(interaction)
                except NotAdmin as e:
                    await e.send_error_message(interaction)
            try:
                if (choices.value == "add"):
                    embed.add_field(name="추가/제거", value="추가")
                elif(choices.value == "remove"):
                    embed.add_field(name="추가/제거", value="제거")
                    
                if(role.value == "admin"):
                    embed.add_field(name="권한", value="관리자")
                elif(role.value == "DB_admin"):
                    embed.add_field(name="권한", value="DB 관리자")
                embed.add_field(name="고유번호", value=f"{personalnum}", inline=False)
                embed.set_footer(text="정상적으로 처리되었습니다 Made By Mebo")
            except:
                embed = discord.Embed(title="커맨드 오류",
                color=discord.Color.red())
                embed.add_field("오류 분류",value="DB 오류",inline=False)
                embed.add_field("오류 내용",value=e,inline=False)
                await interaction.response.send_message(embed=embed,ephemeral=True)
            finally:
                channel = self.bot.get_channel(1259715536967958659)
                e = discord.Embed(title="메보 이케아 권한관리 로그",color=discord.Color.green())
                if (choices.value == "add"):
                    e.add_field(name="추가/제거", value="추가")
                elif(choices.value == "remove"):
                    e.color=discord.Color.red()
                    e.add_field(name="추가/제거", value="제거")
                    
                if(role.value == "admin"):
                    e.add_field(name="권한", value="관리자")
                elif(role.value == "DB_admin"):
                    e.add_field(name="권한", value="DB 관리자")
                e.add_field(name="대상자 고유번호", value=f"{personalnum}", inline=False)
                e.add_field(name="담당자", value=f"{interaction.user.nick}({interaction.user.id}", inline=False)
                e.set_footer(text="정상적으로 처리되었습니다 Made By Mebo")
                await channel.send(embed=e)
                connection.close()
                await interaction.response.send_message(embed=embed,ephemeral=True)
                
        except Exception as e:
            embed = discord.Embed(title="커맨드 오류",
                        color=discord.Color.red())
            embed.add_field("오류 분류",value="DB 오류",inline=False)
            embed.add_field("오류 내용",value=e,inline=False)
            await interaction.response.send_message(embed=embed,ephemeral=True)
            return
        finally:
            connection.close()
    



async def setup(bot):
    await bot.add_cog(permission(bot),
                        guilds=[discord.Object(id=1184482371047800892)])

        
    
