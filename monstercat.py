import aiohttp
import asyncio

from bs4 import BeautifulSoup

class Client():
    def __init__(self, *, loop=None):
        self._headers: Dict[str, str] = {
            "User-Agent": "monstercatFM.py (https://github.com/Zenrac/monstercatFM.py)",
            "Content-Type": "application/json",
        }     
        self.url = "https://mctl.io/"
        self.handler = None
        self._loop = loop or asyncio.get_event_loop()
        self.now_playing = None
        
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
        
    async def transform_html(self, resp):
        """Makes html readable with BeautifulSoup and returns current track"""
        text = await resp.read()
        text = BeautifulSoup(text, 'lxml')
        text = text.find_all("p", {"name":"np-element"})
        result = []
        for tex in text:
            if tex.text not in result: # avoid info occurrences
                if 'by ' in tex.text:  
                    result.append(tex.text.replace('by ', ''))
                else:
                    result.append(tex.text)
        return result[1:3]    
        
    async def get_current_track(self):
        """Gets the current track informations"""    
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.get(self.url) as resp:
                if resp.status == 200:
                    return await self.transform_html(resp)

    async def start(self):
        while True:
            if self.handler:
                current = await self.get_current_track()
                if current != self.now_playing: # ignore if we already have the info
                    before = self.now_playing # don't wait if before was None (during first loop)
                    self.now_playing = current 
                    await self.handler(current)
                    if before:
                        await asyncio.sleep(60) # Wait a min after updating song (assuming a song duration > 60)
                await asyncio.sleep(1)  # get info every sec, I don't know if it is useful / if I should put more
                                        # and I don't even know if using a aiohttp.get loop is a good idea
                                        # I tried to use websocket and socket.io, in vain. (lack of skills/knowledges ?)
            else:
                raise RuntimeError("No function handler specified")    

    def register_handler(self, handler):
        """Registers a function handler to allow you to do something with the socket API data"""
        self.handler = handler     
