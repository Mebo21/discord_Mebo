"""
Copyright (c) 2024 메보
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import discord
from discord.ext import commands, tasks
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
class BlacklistCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_blacklist.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print('이케아 블랙확인 시스템이 로드 되었습니다.')
    
    @tasks.loop(minutes=1)
    async def check_blacklist(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
        channel1 = self.bot.get_channel(1268806873818206242)
        await channel1.send(f"현재 프로그램 내부 시각 : {now}")
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM blacklist WHERE RemoveDate=%s", (now,))
                users_to_remove = cursor.fetchall()
                for user in users_to_remove:
                    cursor.execute("DELETE FROM blacklist WHERE PersonalNum=%s", (user['PersonalNum'],))
                    channel = self.bot.get_channel(1268802368351240323)
                    e = discord.Embed(title="메보 이케아 블랙리스트 해제 알림", color=discord.Color.green())
                    e.add_field(name="대상자 정보", value=f"{user['PersonalNum']} | {user['Nickname']}", inline=False)
                    e.add_field(name="해제 일시", value=now, inline=False)
                    e.set_footer(text="정상적으로 처리되었습니다 Made By Mebo")
                    await channel.send(embed=e)
            connection.commit()
        finally:
            connection.close()

    @check_blacklist.before_loop
    async def before_check_blacklist(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BlacklistCheck(bot), guilds=[discord.Object(id=1184482371047800892)])
