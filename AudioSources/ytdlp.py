from yt_dlp import YoutubeDL
from yt_dlp.extractor.soundcloud import SoundcloudIE

class youtube:
    def __init__(self, query: str, platform: str, download = False, playliststart = 1, playlistend = 1):
        self.query = query
        self.platform = platform
        self.download = download
        self.ytdlopts = {
            'default_search': 'auto',
            'format': 'bestaudio/best',
            'outtmpl': "downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s",
            'noplaylist': False,
            'playliststart': playliststart,
            'playlistend': playlistend,
            'skip_unavailable_fragments': True,
            'geo_bypass': True,
            'source_address': '0.0.0.0',
            'force-ipv4': True,
            #'force-ipv6': True,
            #'proxy': 'http://user:pass@x.x.x.x:port',
            'rm_cachedir': True,
            'cachedir': False,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True
        }

    def getinfo(self):
        with YoutubeDL(self.ytdlopts) as _youtube:
            print(f"[YoutubeDL] platform `{self.platform}`")
            if self.platform is not None:
                if self.platform == 'auto':
                    ie_key = None
                elif self.platform == 'Soundcloud':
                    ie_key = SoundcloudIE.ie_key() # Only works with soundcloud links
                else:
                    ie_key = None
            try:
                self.info = _youtube.extract_info(
                    url = self.query,
                    download = self.download,
                    ie_key = ie_key
                )
            except Exception as e:
                print(f"yt-dlp exception: {e}")
                return None
            if self.info is not None:
                # if query was either a string or a link of a playlist -> retrieve dict
                entries = self.info.get('entries')
                # if query was a link -> retrieve list
                if entries is None:
                    entries = []
                    entries.append(self.info)
                return entries