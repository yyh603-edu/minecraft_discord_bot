from core.classes import Cog_Extension
from discord.ext import commands

class EasterEgg(Cog_Extension):

    @commands.Cog.listener()
    async def on_ready(self):
        print('easteregg is ready')
        
    @commands.command()
    async def 小丑(self, ctx):
        await ctx.send(f"<@{719096615465517058}> 是小丑🤡")

    @commands.command()
    async def starburst(self, ctx):
        await ctx.send('星爆氣流斬！！！！！！ https://media.discordapp.net/attachments/930801532566401064/1109403857471160440/scLsqQC.gif')
async def setup(bot):
    await bot.add_cog(EasterEgg(bot))