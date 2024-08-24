import asyncio
import copy
from AudioSources import ytdlp

class sourcecls:
    
    def __init__(self, requestor: str, query: str, platform: str, source_info: dict):
        self.requestor = requestor
        self.query = query
        self.platform = platform
        print(f"[sourcecls] platform `{self.platform}`")
        if source_info is None:
            self.source_info = {
                'requestor': self.requestor,
                'query': self.query,
                'platform': self.platform,
                'source_type': None,
                'source': None,
                'playlist_count': None
            }
        else:
            self.source_info = source_info

    def get(self, playliststart = 1, playlistend = 1):
        source_list = []
        entries = ytdlp.youtube(
                        query = self.query,
                        platform = self.platform,
                        download = False,
                        playliststart = playliststart,
                        playlistend = playlistend
                    ).getinfo()
        if not entries:
            return source_list
        for entry in entries:
            if entry is None:
                continue
            self.source_info['source'] = {
                'title': entry.get('title'),
                'webpage_url': entry.get('webpage_url'),
                'url': entry.get('url'),
                'duration': entry.get('duration'),
                'playlist_count': entry.get('playlist_count')
            }
            # check if valid?
            source_list.append(
                copy.deepcopy(
                    self.source_info
                )
            )
        return source_list

    def refresh(self) -> bool:
        if self.isValid():
            print("Refreshing source...")
            _source_info = ytdlp.youtube(
                                query = self.source_info['source'].get('webpage_url'),
                                platform = self.source_info['platform'],
                                download = False
                            ).getinfo()
            self.source_info['source']['url'] = str(_source_info[0].get('url'))
        else:
            print("Invalid source (refresh)")
        return self.isValid()

    def isValid(self) -> bool:
        if (
                isinstance(self.source_info, dict) and
                self.source_info.get('source') is not None and
                self.source_info['source'].get('webpage_url') is not None and
                self.source_info['source'].get('url') is not None
        ):
            return True
        else:
            print("Invalid source")
            if not isinstance(self.source_info, dict):
                print("self.source_info is not a dict")
            else:
                if self.source_info.get('source') is None:
                    print("self.source_info.get('source') is None")
                else:
                    if self.source_info['source'].get('webpage_url') is None:
                        print("self.source_info['source'].get('webpage_url') is None")
                    if self.source_info['source'].get('url') is None:
                        print("self.source_info['source'].get('url') is None")
        return False