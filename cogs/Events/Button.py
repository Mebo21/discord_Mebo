"""
Copyright (c) 2024 메보
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import configs
import discord
from discord import app_commands ,Interaction,ui,ButtonStyle,SelectOption,Webhook,Colour,Embed
from discord.ext import commands
import os
import aiohttp
from flask import Flask, request, jsonify, session
import pymysql
from flask_cors import CORS
import random
import datetime
import asyncio


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

class PermissionButtons(discord.ui.View):
        def __init__(self,pn:str,name:str,message: discord.Message, bot:commands.Bot):
            super().__init__(timeout=1000000)
            self.pn = pn
            self.name = name
            self.message = message
            self.bot = bot
        
        @discord.ui.button(label="허가",style=discord.ButtonStyle.green)
        async def allow(self,ctx:discord.Interaction,button:discord.ui.Button):
            channel =  self.bot.get_channel(1256650292427100231)
            
            e = discord.Embed(title="사용자 허가 로그",color=discord.Color.green())
            e.add_field(name="고유번호", value=f"{self.pn}")
            e.add_field(name="닉네임", value=f"{self.name}")
            e.add_field(name="담당자 정보", value=f"{ctx.user.nick}( {ctx.user.id} )")
            e.set_footer(text="Made by Mebo")
            e.timestamp=datetime.datetime.now()
            await self.message.add_reaction("✅")
            await ctx.message.delete()
            await channel.send(embed=e)
            
            try:
                connection = get_db_connection()
                with connection.cursor() as cursor:
                    query = 'UPDATE user SET Permission = 1 WHERE PersonalNum = %s'
                    cursor.execute(query,(self.pn,))
                    connection.commit()
            except Exception as e:
                print('DB 오류 :',e)
            finally:
                connection.close()
            
        @discord.ui.button(label="불허",style=discord.ButtonStyle.red)
        async def noallow(self,ctx:discord.Interaction,button:discord.ui.Button):
            channel = self.bot.get_channel(1258453672673804360)
            
            e = discord.Embed(title="사용자 거부 로그",color=discord.Color.red())
            e.add_field(name="고유번호", value=f"{self.pn}")
            e.add_field(name="닉네임", value=f"{self.name}")
            e.add_field(name="담당자 정보", value=f"{ctx.user.nick}( {ctx.user.id} )")
            e.set_footer(text="Made by Mebo")
            e.timestamp=datetime.datetime.now()
            await self.message.add_reaction("✅")
            await ctx.message.delete()
            await channel.send(embed=e)
            
            try:
                connection = get_db_connection()
                with connection.cursor() as cursor:
                    query = f'UPDATE user SET Permission = -1 WHERE PersonalNum = %s'
                    cursor.execute(query,(self.pn,))
                    connection.commit()
            except Exception as e:
                print('DB 오류 :',e)
            finally:
                connection.close()

class permissionBTN(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,msg):
        if msg.author.bot and msg.author.id != 1256650741246984284:
            return
        if msg.channel.id == 1256650213427249192:
            embeds = msg.embeds
            for embed in embeds:
                pn = embed.to_dict()['fields'][0]['value']
                name = embed.to_dict()['fields'][1]['value']
            allowed_mentions = discord.AllowedMentions(everyone = True)
            await msg.reply("@everyone",view=PermissionButtons(pn,name,msg,self.bot),allowed_mentions = allowed_mentions)
        
async def setup(bot):
    await bot.add_cog(permissionBTN(bot))
