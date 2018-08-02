import aiohttp
import asyncio

from bs4 import BeautifulSoup

class Client():
    def __init__(self, loop=None):
        self._headers: Dict[str, str] = {
            "User-Agent": "monstercatFM (https://github.com/Zenrac/monstercatFM)",
            "Content-Type": "application/json",
        }     
        self.url = "https://mctl.io/"
        self.handler = None
        self._loop = loop or asyncio.get_event_loop()
        self.now_playing = None
        self.ready = False
        self.counter = 0
        
    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop    

    async def get_old_tracks(self, nb=None):
        """Gets previous tracks, can load 15, 25, 50 or 100 tracks other number returns 15."""
        if nb in [25, 50, 100]:
            url = self.url + "?l={}".format(nb) # f-string only supported on py3.6+
        else:
            url = self.url 
        
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    text = await resp.read()
                    text = BeautifulSoup(text, 'lxml')  
                    text = text.find_all("tr")
                    result = []
                    for tex in text:
                        result.append(tex.text.replace('\n', '|'))
                    results = result[1:]  
                    
                    data = []
                    for res in results:
                        ordered = []
                        occs = res.split('|')
                        for occ in occs:
                            if occ and ('http' not in occ and not occ[1:2].isdigit()):
                                ordered.append(occ)
                        data.append(ordered)
                    return data
        
    async def transform_html(self, text):
        """Makes html readable with BeautifulSoup and returns current track"""
        text = BeautifulSoup(text, 'lxml')
        text = text.find_all("p", {"name":"np-element"})
        result = []
        for tex in text:
            if tex.text not in result: # avoid info occurrences
                if 'by ' in tex.text:  
                    result.append(tex.text.replace('by ', ''))
                else:
                    result.append(tex.text)          
        return result[1:]    
        
    async def get_duration(self, text):
        """Gets duration from HTML with BeatifulSoup"""
        text = BeautifulSoup(text, 'lxml')
        text = text.find(id="duration")
        return int(text.text)
            
    async def get_current_track(self):
        """Gets the current track informations"""    
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.get(self.url) as resp:
                if resp.status == 200:
                    text = await resp.read()
                    duration = await self.get_duration(text)
                    data = await self.transform_html(text)
                    return data, duration

    async def start(self):
        while True:
            if self.handler:
                current, duration = await self.get_current_track()
                if current != self.now_playing: # ignore if we already have the info
                    before = self.now_playing # don't wait if before was None (during first loop)
                    self.now_playing = current 
                    await self.handler(current)
                    if before:
                        self.ready = True
                        self.counter = 0
                        time = min((duration/1000), 600) # can't be more than 10 mins, I think
                        time -= 2 # Better finishing before song update
                        await asyncio.sleep(time)
                if self.ready:                   
                    if self.counter >= 1: # Wow, already made 10 requests ? Calm down. 
                        time = min(3, self.counter)
                    else:
                        time = 0.1
                        self.counter += time                       
                    await asyncio.sleep(time) 
                else:
                    await asyncio.sleep(1) # get info every sec until we are sync with songs durations etc... 
            else:
                raise RuntimeError("No function handler specified")    

            # I don't even know if using a aiohttp.get loop is a good idea
            # I tried to use websocket and socket.io, in vain. (lack of skills/knowledges ?)

    def register_handler(self, handler):
        """Registers a function handler to allow you to do something with the socket API data"""
        self.handler = handler     
