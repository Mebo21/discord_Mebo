import discord
from discord import app_commands
from discord.ext import commands
import pymysql
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

class Blacklist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('이케아 블랙리스트 시스템이 로드 되었습니다.')
        
    @app_commands.command(name="블랙리스트_명단", description="블랙리스트 명단을 확인합니다.")
    async def list_blacklist(self,interaction: discord.Interaction):
        embed = discord.Embed(title="메보 이케아 블랙리스트 명단", color=discord.Color.green())
        embed.timestamp = datetime.datetime.now()
        try:
            admin_role_id = 1184492586828832890
            if interaction.user.guild_permissions.administrator or discord.utils.get(interaction.user.roles, id=admin_role_id):
                connection = get_db_connection()
                with connection.cursor() as cursor:
                    query = "SELECT * FROM blacklist"
                    cursor.execute(query)
                    black_list = cursor.fetchall()
                    for black in black_list:
                        embed.add_field(name=f"{black['PersonalNum']} | {black['Nickname']}",value=f"사유: {black['Reason']} \n해제 일시: {black['RemoveDate']}")
                    await interaction.response.send_message(embed=embed,ephemeral=True)
                    
        except Exception as e:
            print(e)
        finally:
            connection.close()
    
    @app_commands.command(name="블랙리스트_등록", description="블랙리스트에 사용자를 등록합니다.")
    async def add_blacklist(self, interaction: discord.Interaction,
                            personalnum: int, nickname: str, day: int, reason: str):
        embed = discord.Embed(title="메보 이케아 권한관리 시스템", color=discord.Color.green())
        embed.timestamp = datetime.datetime.now()
        AdminList = [interaction.guild.owner_id, 381620167160889364]

        try:
            admin_role_id = 1184492586828832890
            if interaction.user.guild_permissions.administrator or discord.utils.get(interaction.user.roles, id=admin_role_id):
                connection = get_db_connection()
                with connection.cursor() as cursor:
                    query = "SELECT * FROM blacklist WHERE PersonalNum=%s"
                    cursor.execute(query, (personalnum,))
                    user = cursor.fetchone()
                    if user:
                        await interaction.response.send_message(
                            embed=discord.Embed(
                                title="커맨드 오류",
                                description="이미 블랙리스트에 등록되어있는 사용자 입니다.",
                                color=discord.Color.red()
                            ), ephemeral=True
                        )
                        return

                with connection.cursor() as cursor:
                    now = datetime.datetime.now()
                    RemoveDate = now + datetime.timedelta(days=day)
                    cursor.execute(
                        "INSERT INTO blacklist(PersonalNum, Nickname, Reason, RemoveDate) VALUES (%s, %s, %s, %s)",
                        (personalnum, nickname, reason, RemoveDate.strftime("%Y-%m-%d_%H:%M"))
                    )
                    connection.commit()
            else:
                raise NotAdmin()

            try:
                channel = self.bot.get_channel(1268802368351240323)
                e = discord.Embed(title="메보 이케아 블랙리스트 로그", color=discord.Color.green())
                e.add_field(name="등록/해제", value="등록")
                e.add_field(name="대상자 정보", value=f"{personalnum} | {nickname}")
                e.add_field(name="등록 사유", value=reason)
                e.add_field(name="해제 일시", value=RemoveDate.strftime("%Y년%m월%d일 %H시%M분"))
                e.add_field(name="담당자", value=f"{interaction.user.nick}({interaction.user.id})")
                e.set_footer(text="정상적으로 처리되었습니다 Made By Mebo")
                await channel.send(embed=e)

                embed.add_field(name="고유번호", value=f"{personalnum}")
                embed.set_footer(text="정상적으로 처리되었습니다 Made By Mebo")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                embed = discord.Embed(title="커맨드 오류", color=discord.Color.red())
                embed.add_field(name="오류 분류", value="기타 오류", inline=False)
                embed.add_field(name="오류 내용", value=str(e), inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        except NotAdmin as e:
            await e.send_error_message(interaction)
        except Exception as e:
            embed = discord.Embed(title="커맨드 오류", color=discord.Color.red())
            embed.add_field(name="오류 분류", value="DB 오류", inline=False)
            embed.add_field(name="오류 내용", value=str(e), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        finally:
            connection.close()

    @app_commands.command(name="블랙리스트_해제", description="블랙리스트에서 사용자를 해제합니다.")
    async def remove_blacklist(self, interaction: discord.Interaction,
                                personalnum: int, reason: str):
        embed = discord.Embed(title="메보 이케아 권한관리 시스템", color=discord.Color.green())
        embed.timestamp = datetime.datetime.now()
        AdminList = [interaction.guild.owner_id, 381620167160889364]

        try:
            admin_role_id = 1184492586828832890
            if interaction.user.guild_permissions.administrator or discord.utils.get(interaction.user.roles, id=admin_role_id):
                connection = get_db_connection()
                with connection.cursor() as cursor:
                    query = "SELECT * FROM blacklist WHERE PersonalNum=%s"
                    cursor.execute(query, (personalnum,))
                    user = cursor.fetchone()
                    if user:
                        cursor.execute("DELETE FROM blacklist WHERE PersonalNum=%s", (personalnum,))
                        connection.commit()
                    else:
                        await interaction.response.send_message(
                            embed=discord.Embed(
                                title="커맨드 오류",
                                description="블랙리스트에 등록되어있지 않은 사용자 입니다.",
                                color=discord.Color.red()
                            ), ephemeral=True
                        )
                        return
            else:
                raise NotAdmin()

            try:
                channel = self.bot.get_channel(1268802368351240323)
                e = discord.Embed(title="메보 이케아 블랙리스트 로그", color=discord.Color.red())
                e.add_field(name="등록/해제", value="해제")
                e.add_field(name="대상자 정보", value=f"{personalnum}")
                e.add_field(name="해제 사유", value=reason)
                e.add_field(name="담당자", value=f"{interaction.user.nick}({interaction.user.id})")
                e.set_footer(text="정상적으로 처리되었습니다 Made By Mebo")
                await channel.send(embed=e)

                embed.add_field(name="고유번호", value=f"{personalnum}")
                embed.set_footer(text="정상적으로 처리되었습니다 Made By Mebo")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                embed = discord.Embed(title="커맨드 오류", color=discord.Color.red())
                embed.add_field(name="오류 분류", value="기타 오류", inline=False)
                embed.add_field(name="오류 내용", value=str(e), inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        except NotAdmin as e:
            await e.send_error_message(interaction)
        except Exception as e:
            embed = discord.Embed(title="커맨드 오류", color=discord.Color.red())
            embed.add_field(name="오류 분류", value="DB 오류", inline=False)
            embed.add_field(name="오류 내용", value=str(e), inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        finally:
            connection.close()

async def setup(bot):
    await bot.add_cog(Blacklist(bot), guilds=[discord.Object(id=1184482371047800892)])
