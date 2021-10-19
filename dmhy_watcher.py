
import os, sys
import json
from time import mktime
import re
import feedparser
from bs4 import BeautifulSoup
from My_Logger import *
from discord_msg_util import send_message


# global variables
CONFIG:dict
WATCHLIST:list
NEW_BUNGUMIS:list = []

CONFIG_TEMPLATE:dict = {
    "post_fetch_cmd": None,
    "fifo_filepath": None
}

WATCHLIST_UNIT:dict = {
    "rss_url": "",
    "regex_pattern": "",
    "latest_episode": 0
}


# functions

def load_config():
    global CONFIG
    try:
        if os.path.isfile("config.json"):
            with open("config.json", 'r', encoding="utf-8") as configfile:
                CONFIG = json.load(configfile)
        else:
            init_config()
            with open("config.json", 'r', encoding="utf-8") as configfile:
                CONFIG = json.load(configfile)
        
    except Exception as err: # Unable to load config.json
        broadcastErrorMsg(f"Unable to load config.json because: {err}")
        raise err

def init_config():
    with open("config.json", 'w', encoding="utf-8") as configfile:
        json.dump(CONFIG_TEMPLATE, configfile, ensure_ascii=False)

def load_watchlist():
    global WATCHLIST
    try:
        if os.path.isfile("watchlist.json"):
            with open("watchlist.json", 'r', encoding="utf-8") as watchlistfile:
                WATCHLIST = json.load(watchlistfile)
        else: # watchlist.json does not exists
            init_watchlist()
            with open("watchlist.json", 'r', encoding="utf-8") as watchlistfile:
                WATCHLIST = json.load(watchlistfile)
        
    except Exception as err: # Unable to load watchlist.json
        broadcastErrorMsg(f"Unable to load watchlist.json because: {err}")
        raise err

def init_watchlist():
    with open("watchlist.json", 'w', encoding="utf-8") as watchlistfile:
        json.dump([], watchlistfile, ensure_ascii=False)

def update_watchlist():
    global WATCHLIST
    for bangumi in NEW_BUNGUMIS:
        update_item:dict = WATCHLIST[bangumi['watchlist_idx']]
        update_item.update({"latest_episode":bangumi['episode']})
        WATCHLIST[bangumi['watchlist_idx']] = update_item
    
    with open("watchlist.json", 'w', encoding="utf-8") as watchlistfile:
        json.dump(WATCHLIST, watchlistfile, ensure_ascii=False)

def add_bangumi(rss_url:str = 0, regex_pattern:str = 0, latest_episode:str = 0):
    "Add new Bangumi to watchlist.json"
    
    # setup new watchlist_unit
    new_unit = WATCHLIST_UNIT
    rss_url = input("Please enter rss_url: ") if rss_url == 0 else rss_url
    regex_pattern = input("Please enter regex_pattern: ") if regex_pattern == 0 else regex_pattern
    latest_episode = input("Please enter latest_episode: ") if latest_episode == 0 else latest_episode
    new_unit.update({"rss_url": rss_url})
    new_unit.update({"regex_pattern": regex_pattern})
    new_unit.update({"latest_episode": latest_episode})
    
    # append new unit & write to watchlist
    global WATCHLIST
    WATCHLIST.append(new_unit)
    try:
        with open("watchlist.json", 'w', encoding="utf-8") as watchlistfile:
            json.dump(WATCHLIST, watchlistfile, ensure_ascii=False)
    except Exception as err: # Unable to write to watchlist.json
        broadcastErrorMsg(f"Unable to write to watchlist.json because: {err}")
        raise err


def fetch_rss(rss_url:str, regex_pattern:str, latest_episode:int) -> list:
    """
    fetch all lastest bangumis xml from rss_url that matches regex_pattern
    return list(tuple(int, dict)):
        tuple[0] => latest episode
        tuple[1] => latest bangumi rss feed
    """
    
    res = feedparser.parse(rss_url)
    new_items = []
    match = None
    for item in res.entries:
        match = re.search(regex_pattern, item.title)
        if match is not None:
            episode = int(match.groups()[0])
            if episode > latest_episode:
                new_items.append((episode, item))
    
    return new_items

def fetch_bangumi():
    "fetch bangumi via rss from share.dmhy.org"
    
    if len(CONFIG) == 0:
        broadcastErrorMsg("Empty Config")
        raise ValueError("Empty Config")
    if len(WATCHLIST) == 0:
        broadcastErrorMsg("Empty Watchlist")
        raise ValueError("Empty Watchlist")
    
    global NEW_BUNGUMIS
    for idx, bangumi in enumerate(WATCHLIST):
        latest_bangumi = fetch_rss(bangumi["rss_url"], bangumi["regex_pattern"], bangumi["latest_episode"])
        # cannot find bangumi from rss_url
        if len(latest_bangumi) == 0:
            continue
        else:
            for bang in latest_bangumi:
                NEW_BUNGUMIS.append(
                    {
                        "watchlist_idx": idx,
                        "title": bang[1].title,
                        "episode": bang[0],
                        "link": bang[1].link,
                        "pubDate": int(mktime(bang[1].published_parsed)),
                        "magnet": bang[1].enclosures[0].href
                    }
                )

def post_fetch():
    "post fetch actions if exists: write to fifo, run cmd"
    
    if CONFIG["fifo_filepath"] is not None:
        msg = f"@ New Bangumi update in share.dmhy.org:\n"
        for bangumi in NEW_BUNGUMIS:
            msg += bangumi["title"] + '\n'
        send_message(
            CONFIG["fifo_filepath"],
            msg
        )
    
    if CONFIG["post_fetch_cmd"] is not None:
        os.system(CONFIG["post_fetch_cmd"])

if __name__ == "__main__":
    try:
        # load config.json & watchlist.json
        load_config()
        load_watchlist()
        
        # fetch bangumi & run post fetch cmds
        fetch_bangumi()
        post_fetch()
        
        # post update
        update_watchlist()
        
    except KeyboardInterrupt:
        print()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
