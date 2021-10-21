
# dmhy-watcher

A [share.dmhy.org](http://share.dmhy.org/) Bangumi/Anime following script base on RSS Feed

* While running, this script will search through all RSS Links (supplied by user)
* Once find updated Bangumi, the script will collect basic info of current episode (bangumi title, episode, magnet link, etc...)
* Finally, the script will run user supplied commands

**This script is written for learning. I suggest you to use [弹弹play](http://www.dandanplay.com/) if you have similar demands of following Bangumis**

## [Chinese Versoin](./README.md)

# Python Packages

| Package    | Version |
|------------|---------|
| feedparser | Latest  |

You can run following command to install required packages
```sh
pip install feedparser
```


# Configuration

* Before you execute the script, please have following two json files ready
* You can also run the script first, then fill-in all the info in auto-generated json files

## config.json
* This file is the basic configuration file for the script
* Here is the file template
```json
{
    "post_fetch_cmd": {
        "working_dir": "/path/to/working/directory",
        "cmds": [
            {
                "cmd": "",
                "sleep_time": 0,
                "exec_once": true
            }
        ]
    },
    "fifo_filepath": "/path/to/fifo"
}
```
* post_fetch_cmd: Commands to execute after the script found episode updates on share.dmhy.org
  * working_dir: Working directory while running these commands
  * cmds: Commands
    * This is a JSON list, so you can add/remove any objects in the middle as you want
    * cmd: System commands, the script will use [os.system()](https://docs.python.org/3/library/os.html#os.system) to execute them, default is empty
    * sleep_time: Delay time after command execution, default is 0
    * exec_once: Whether only execute current command once
  * Something to note while writing commands
    * The script will run these commands only after detecting new Bangumi episodes
    * The script will run all commands have exec_once == true first
    * After that, the script will loop through all newly updated Bangumi episodes
    * In each iteration, the script will execute rest of commands which have exec_once == false
    * In each iteration, the script will automatically **REPLACE the first question mark "?" with the MAGNET LINK of current episode**
    * **All commands will be running in main thread, so PLEASE DO NOT WRITE ANY SLOW COMMANDS**
  * fifo_filepath: [fifo](https://linux.die.net/man/4/fifo)'s file path
    * This setting is used to connect with my [another project](https://github.com/Gavin1937/discord-noticmd-bot)
    * While running both projects, this script can automatically notify on specific Discord Server when a Bangumi episode update happens
    * You can enter null for this setting if you don't need this feature
    * Default is null


## watchlist.json
* This file will record your following Bangumis
* Here is the file template
```json
[
    {
        "rss_url": "",
        "regex_pattern": "",
        "latest_episode": 0
    }
]
```
* This is a JSON list, so you can add/remove any objects in the middle as you want
* rss_url: RSS Feed Link
  * [How To Get RSS Link From share.dmhy.org](./dmhy-RSS-tutorial/How-To-Get-RSS-From-dmhy.md#How-to-get-RSS-Link-from-share.dmhy.org)
  * In fact, you don't have to enter a link from share.dmhy.org, as long as it is RSS Link and the number in regex group is increasing, it is fine
  * You can also modify functions fetch_rss() and fetch_bangumi() in [dmhy_watcher.py](./dmhy_watcher.py)
* regex_pattern: [Regular Expression](https://en.wikipedia.org/wiki/Regular_expression) for searching Bangumi episode
  * The script will use this regex to match all the Bangumi Titles
  * If it cannot match anything from title, the script will ignore current episode
  * The script will use regex group to search Bangumi episode
  * **This regex ONLY CAN HAVE ONE GROUP**
  * Some examples
```
Title 1:
【幻櫻字幕組】【10月新番】【古見同學有交流障礙症 Komi-san wa, Komyushou Desu.】【03】【BIG5_MP4】【1920X1080】

Regex 1:
幻櫻字幕組.*古見同學有交流障礙症.*Desu.】【([0-9][0-9]?)】【.*


Title 2:
[波洛咖啡厅\PCSUB][死神少爷与黑女仆\Shinigami Bocchan to Kuro Maid][02][简日][CHS_JP][720P][MP4_AAC][网盘][急招后期]

Regex 2:
波洛咖啡厅.*死神少爷与黑女仆.*Kuro Maid\]\[([0-9][0-9]?)\]\[.*


Title 3:
[桜都字幕組] 小林家的龍女僕S / Kobayashi-san Chi no Maidragon S [03][1080p][繁體內嵌]

Regex 3:
桜都字幕組.*小林家的龍女僕S.*Maidragon S \[([0-9][0-9]?)\]\[.*1080p.*繁體內嵌.*
```
*  * I suggest you use the most important keywords while writing regex: Translation Group + Bangumi Title + Group of Bangumi Episode + Other Requirements (1080p/speciic subtitle)
* latest_episode: Latest episode (if the latest is episode 1, then enter 0), default is 0


# Execute

* Run following command
```sh
python dmhy_watcher.py
```
* If you did not have all the configuration files yet, the script will auto-generate one for you
* I suggest you to run the script first, then enter all info to auto-generated file
* If you already have all the configuration files, the script will try to search for new Bangumi episode, and it will execute all commands in post_fetch_cmd if detected Bangumi episode update
* If the script cannot find any update, it will output
```
Fetching new bangumis...
Updating watchlist.json...
```
* If the script find new updates, it will run all commands in post_fetch_cmd between the two outputs above

