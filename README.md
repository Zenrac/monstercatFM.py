# monstercatFM
Unofficial shitty API wrapper to get informations about the monstercat live stream using [TheAkio's website (MCTL)](https://mctl.io/) and [aiohttp](https://github.com/aio-libs/aiohttp)<br>
I'm a python beginner, I don't really know what I'm doing, your contributions are gladly accepted.<br><br>
### Requirements: <br>
- Python3+<br>
- [aiohttp](https://github.com/aio-libs/aiohttp) <br>
- asyncio<br>
- bs4
### Examples: <br>
Handler to get the current song forever<br>
```py
import asyncio
import monstercat

async def hand(msg):
    print("New song : {} by {}".format(msg[0], msg[1]))  

mc = monstercat.Client() # Can specify a loop if needed

mc.register_handler(hand)
to_run = mc.start()
mc.loop.run_until_complete(to_run)
```
Gets the current song only<br>
```py
import monstercat

mc = monstercat.Client() # Can specify a loop if needed

to_run = mc.get_current_track()
msg = mc.loop.run_until_complete(to_run)

print("New song : {} by {}".format(msg[0], msg[1])) 
```
Gets old already played tracks <br>
```py
import monstercat

requested_tracks = 50

mc = monstercat.Client() # Can specify a loop if needed

to_run = mc.get_old_tracks(requested_tracks)
msg = mc.loop.run_until_complete(to_run)

for i, song in enumerate(msg, start=1):
    print("{} - {} by {}".format(i, song[0], song[1])) 
```
#### Notes:
- If the loop is already running, replace ```run_until_complete(to_run)``` with <br>
```mc.loop.create_task(to_run)```<br>
- Value accepted to get old tracks are : `15, 25, 50, 100` (default is `15`)
