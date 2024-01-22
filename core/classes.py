from discord.ext import commands
import json

class Cog_Extension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

class MyContest:

    def __init__(self, contest=dict(), first_msg=False, second_msg=False):
        self.id = contest['id']
        self.name = contest['name']
        self.duration = contest['durationSeconds']
        self.startTime = contest['startTimeSeconds']
        self.first_msg = first_msg
        self.second_msg = second_msg

    def todict(self):
        ret = dict()
        ret['id'] = self.id
        ret['name'] = self.name
        ret['duration'] = self.duration
        ret['startTime'] = self.startTime
        ret['first_msg'] = self.first_msg
        ret['second_msg'] = self.second_msg
        return ret
    
    def __jsonencode__(self):
        return self.todict()
    


class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__jsonencode__'):
            return obj.__jsonencode__()