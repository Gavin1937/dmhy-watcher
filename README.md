
# dmhy-watcher

一个基于RSS 订阅的[动漫花园](http://share.dmhy.org/)追番脚本

* 在运行时，这个脚本将会检索所有的RSS连接（由用户提供）
* 当找到更新的番剧时，脚本会收集番剧的基本信息（名字、集数、磁链等）
* 最后，脚本将会运行用户指定的命令

**这个脚本是以学习为目的去写的。如果你有类似的追番需求建议使用[弹弹play](http://www.dandanplay.com/)**

## [English Versoin README](./README-en.md)

# Python 版本: >= 3.8
# Python 包

| Package    | Version  |
|------------|----------|
| feedparser | 最新版本  |

你可以运行下面这条指令去安装所需的包
```sh
pip install feedparser
```


# 设置

* 在你运行这个脚本前，请准备好以下两个必要的 json 文件
* 你也可以直接运行脚本，然后在将信息填入自动生成的 json 文件里

## config.json
* 这个文件是脚本的设置文件
* 以下是这个文件的模板
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
* post_fetch_cmd: 在脚本从动漫花园上发现番剧更新之后执行的命令
  * working_dir: 你可以设置这些命令的运行路径，默认为当前路径
  * cmds: 指定的命令
    * 这是一个JSON数组，所以你可以随意的增减中间的对象
    * cmd: 系统命令，脚本会用 [os.system()](https://docs.python.org/zh-cn/3/library/os.html#os.system)去执行这条命令，默认为空
    * sleep_time: 在执行完命令之后的一段延迟时间，默认为 0
    * exec_once: 是否只运行这条命令一遍，默认只运行一遍
  * 在写命令时要注意的事
    * 脚本只会在番剧更新时运行这些命令
    * 脚本会预先运行所有 exec_once == true 的命令
    * 在这之后，脚本会吧所有更新的番剧循环一遍
    * 在每次循环中，脚本会运行剩下的 exec_once == false 的命令
    * 在每次循环中运行前，脚本会自动把指令里面的**第一个问号 "?" 替换成当前番剧的磁链**再运行（如果没有问号就会直接运行）
    * **所有的指令都是在主线程上运行的，所以请不要写一些运行得很慢的命令**
  * fifo_filepath: [fifo](https://linux.die.net/man/4/fifo) 的文件路径。
    * 这条设置是用来关联我[另外一个项目](https://github.com/Gavin1937/discord-noticmd-bot)的
    * 当两个项目同时运行时，这个脚本可以在番剧更新时自动发信息提醒指定的 Discord Server
    * 如果不需要这个功能可以直接填 null
    * 默认为 null


## watchlist.json
* 这个文件将记录你想追的番剧
* 以下是这个文件的模板
```json
[
    {
        "rss_url": "",
        "regex_pattern": "",
        "latest_episode": 0
    }
]
```
* 这是一个JSON数组，所以你可以随意的增减中间的对象
* rss_url: RSS 订阅链接
  * [如何获取动漫花园 RSS 链接](./dmhy-RSS-tutorial/How-To-Get-RSS-From-dmhy.md#如何从动漫花园获取-RSS-链接)
  * 其实不一定要是动漫花园的链接，只要是 RSS 链接并且正则表达式的分组数字在增长就行了
  * 你也可以自己修改[dmhy_watcher.py](./dmhy_watcher.py)里面的 fetch_rss() 和 fetch_bangumi() 两个函数
* regex_pattern: 用于搜索番剧集数的[正则表达式](https://baike.baidu.com/item/%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F/1700215#:~:text=%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%98%AF%E5%AF%B9%E5%AD%97%E7%AC%A6%E4%B8%B2%EF%BC%88%E5%8C%85%E6%8B%AC%E6%99%AE%E9%80%9A%E5%AD%97%E7%AC%A6,%E6%88%96%E5%A4%9A%E4%B8%AA%E5%AD%97%E7%AC%A6%E4%B8%B2%E3%80%82)
  * 脚本会用这条正则表达式去搜索所有番剧的标题
  * 如果无法从当前番剧标题中搜索到任何东西，脚本会跳过当前番剧
  * 脚本会用正则表达式的分组功能去搜索番剧集数
  * **这个正则表达式只能有一个分组**
  * 一些例子
```
标题 1:
【幻櫻字幕組】【10月新番】【古見同學有交流障礙症 Komi-san wa, Komyushou Desu.】【03】【BIG5_MP4】【1920X1080】

正则表达式 1:
幻櫻字幕組.*古見同學有交流障礙症.*Desu.】【([0-9][0-9]?)】【.*


标题 2:
[波洛咖啡厅\PCSUB][死神少爷与黑女仆\Shinigami Bocchan to Kuro Maid][02][简日][CHS_JP][720P][MP4_AAC][网盘][急招后期]

正则表达式 2:
波洛咖啡厅.*死神少爷与黑女仆.*Kuro Maid\]\[([0-9][0-9]?)\]\[.*


标题 3:
[桜都字幕組] 小林家的龍女僕S / Kobayashi-san Chi no Maidragon S [03][1080p][繁體內嵌]

正则表达式 3:
桜都字幕組.*小林家的龍女僕S.*Maidragon S \[([0-9][0-9]?)\]\[.*1080p.*繁體內嵌.*
```
*  * 建议在搜索时加入最重要的关键词: 字幕组 + 番剧名 + 番剧集数的分组 + 其他要求（1080p、简体字幕）
* latest_episode: 最新的番剧集数（如果最新的是第一集的话就填 0 ），默认为 0


# 运行

* 运行下面这条命令
```sh
python dmhy_watcher.py
```
* 如果你还没准备好设置文件的话，脚本会自动生成一份
* 建议直接运行脚本然后在将信息填入生成的设置文件里
* 如果你已经准备好设置文件的话，脚本会尝试搜索番剧更新，如果有更新就会执行在 post_fetch_cmd 里面的命令
* 如果脚本没有找到新的番剧更新的话，会显示
```
Fetching new bangumis...
Updating watchlist.json...
```
* 如果脚本找到了新的番剧更新，会在着两条中间运行你写的 post_fetch_cmd 
* 你可以用系统自带的定时自动运行功能去跑这个脚本
  * [Windows Task Schedular](https://www.jianshu.com/p/4e44d480fddd)
  * [Linux/MacOS Crontab](https://www.runoob.com/w3cnote/linux-crontab-tasks.html)
