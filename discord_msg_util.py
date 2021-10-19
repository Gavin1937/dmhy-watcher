
# Simple Utility Functions for working with discord-noticmd-bot
# Import this file to other python scripts to interact with discrod-noticmd-bot

import os

def send_message(fifopath:str, message:str) -> None:
    """
    @Param: fifopath:  => string path to discord_noticmd_bot fifo
    @Param: message:   => utf-8 string message write to fifo
                          If message start with "@ " (e.g. "@ new messages...")
                          discord-noticmd-bot.py will mention the admin in this message.
                          Be sure to include both '@' and ' ' charaters
    """
    if os.path.exists(fifopath):
        with open(fifopath, 'w', encoding="utf-8") as fifo:
            fifo.write(message)
    else:
        raise ValueError("Please input a valid fifopath")

