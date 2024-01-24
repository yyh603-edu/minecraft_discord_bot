from core.classes import Cog_Extension
from discord.ext import commands
import json
import os
from mcstatus import JavaServer
import datetime
import socket
import requests
import time


HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.environ['DIGITALOCEAN_API_TOKEN'],
}

SSH_KEYS = os.getenv("SSH_KEYS")

class Droplet:
    def __init__(self):
        self.id = ""
        self.status = ""
        self.ip_addr = ""
        self.update()
    def update(self):
        url = "https://api.digitalocean.com/v2/droplets?page=1&per_page=2"
        response = requests.get(url, headers = HEADERS)
        # print(response.status_code)
        content = json.loads(response.content)
        # print(content)
        # print(len(content["droplets"]))
        if len(content["droplets"]) == 1:
            self.id = ""
            self.status = ""
            self.ip_addr = ""
            return
        else:
            tarserver = content["droplets"][0]
            for server in content['droplets']:
                if server['name'] != "minecraft-discord-bot":
                    tarserver = server
            self.id = tarserver['id']
            self.status = tarserver['status']
            for address in tarserver["networks"]["v4"]:
                if address["type"] == "private":
                    continue
                else:
                  self.ip_addr = address["ip_address"]
            return
    def get_id(self):
        self.update()
        return self.id

    def get_status(self):
        self.update()
        return self.status

    def get_address(self):
        self.update()
        return self.ip_addr

    def shutdown(self): # and make snapshot and delete
        self.update()
        url = (
            "https://api.digitalocean.com/v2/droplets/"
            + str(self.get_id())
            + "/actions"
        )
        payload = {"type": "shutdown"}
        response = requests.post(url, headers = HEADERS, data = json.dumps(payload))
        print(response.status_code)
        content = json.loads(response.content)
        action = content["action"]["id"]
        url = "https://api.digitalocean.com/v2/actions/" + str(action)
        counter = 1
        while True:
            response = requests.get(url, headers = HEADERS)
            content = json.loads(response.content)
            if content["action"]["status"] == "completed":
                break
            elif counter > 120:
                return False
            else:
                counter += 1
                time.sleep(5)
        url = (
            "https://api.digitalocean.com/v2/droplets/"
             + str(self.get_id())
             + "/actions"
        )
        print("server close")
        payload = {
            "type": "snapshot",
            "name": "yyhsnapshot_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        }
        response = requests.post(url, headers = HEADERS, data = json.dumps(payload))
        content = json.loads(response.content)
        action = content["action"]["id"]
        url = "https://api.digitalocean.com/v2/actions/" + str(action)
        counter = 1
        while True:
            response = requests.get(url, headers = HEADERS)
            content = json.loads(response.content)
            if content["action"]["status"] == "completed":
                break
            elif counter > 120:
                return False
            else:
                counter += 1
                time.sleep(5)
        print('snapshot success')  
        url = "https://api.digitalocean.com/v2/droplets/" + str(self.get_id())
        response = requests.delete(url, headers = HEADERS)
        print(response.status_code)
        if response.status_code == 204:
            return True
        else:
            return False

class Snapshot:
  
    def __init__(self):
        self.id = ""
        self.update()

    def update(self):
        url = "https://api.digitalocean.com/v2/snapshots?page=1&per_page=100&resource_type"
        response = requests.get(url, headers = HEADERS)
        content = json.loads(response.content)
        if not content.get("snapshots"):
            self.id = ""
            return
        else:
            # tar = content["snapshots"][0]
            for snapshot in content["snapshots"]:
                if 'yyh' not in snapshot["name"]:
                    self.id = snapshot["id"]
            return
    def get_id(self):
        self.update()
        return self.id

    def create_droplet(self):
        self.update()
        url = "https://api.digitalocean.com/v2/droplets"
        payload = {
            "name": "Myserver",
            "region": "sgp1",
            "size": "s-2vcpu-2gb",
            "image": self.id,
            "ssh_keys": "0b:83:7e:b4:02:6a:b2:bf:88:a5:6c:04:27:f2:85:bb",
        }
        response = requests.post(url, headers = HEADERS, data = json.dumps(payload))
        if response.status_code == 202:
            return True
        else:
            return False


droplet = Droplet()
snapshot = Snapshot()

def get_server():
    print(droplet.get_address())
    try:
        server = JavaServer.lookup(droplet.get_address())
    except Exception as e:
        print(e)
        return
    return server


class server_operation(Cog_Extension):

    @commands.Cog.listener()
    async def on_ready(self):
        print('server_operation is ready')


    @commands.command()
    async def start(self, ctx):
        print("!start")
        if droplet.get_id():
            print("exist")
            try:
                server = get_server()
                status = server.status()
                
                await ctx.send("伺服器目前開著，IP:" + droplet.get_address() + ":25565")
            except socket.timeout:
                await ctx.send("伺服器目前開啟中")
            except Exception as e:
                await ctx.send(f"發生問題 <@{719096615465517058}> " + e)
                return
        else:
            try:
              success = snapshot.create_droplet()
            except Exception as e:
                print(e)
                return
            if success:
                await ctx.send("伺服器正在開啟，請稍等")
                counter = 1
                while True:
                    try:
                        server = get_server()
                        status = server.status()
                        counter += 1
                        time.sleep(10)
                        break
                    except Exception as e:
                        if counter > 60:
                            await ctx.send(f"發生問題 <@{719096615465517058}> " + e)
                            return
                        else:
                            continue
                await ctx.send("伺服器開啟成功，IP:" + droplet.get_address() + ":25565")
            else:
                await ctx.send(f"發生問題 <@{719096615465517058}>")
                return
    
    @commands.command()
    async def stop(self, ctx):
        print('!stop')
        if not droplet.get_id():
            await ctx.send("伺服器已經是關閉狀態")
        else:
            try:
                print('test1')
                server = get_server()
                print('test2')
                print(server.status())
                print('test3')
                status = server.status()
                if status.players.online:
                    await ctx.send("伺服器目前有玩家在玩")
                else:
                    await ctx.send("伺服器正在關閉中，請稍等")
                    success = droplet.shutdown()
                
                if success:
                    await ctx.send("伺服器關閉成功")
                else:
                    await ctx.send(f"伺服器關閉失敗， <@{719096615465517058}>")
            except socket.timeout:
                await ctx.send("伺服器目前開啟中，開啟後再關閉")
                return
            except Exception as e:
                await ctx.send(f"發生問題 <@{719096615465517058}> " + e)
                return
                

async def setup(bot):
    await bot.add_cog(server_operation(bot))