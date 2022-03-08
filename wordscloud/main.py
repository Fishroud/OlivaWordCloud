'''
 __     __     ______     ______     _____     ______     __         ______     __  __     _____    
/\ \  _ \ \   /\  __ \   /\  == \   /\  __-.  /\  ___\   /\ \       /\  __ \   /\ \/\ \   /\  __-.  
\ \ \/ ".\ \  \ \ \/\ \  \ \  __<   \ \ \/\ \ \ \ \____  \ \ \____  \ \ \/\ \  \ \ \_\ \  \ \ \/\ \ 
 \ \__/".~\_\  \ \_____\  \ \_\ \_\  \ \____-  \ \_____\  \ \_____\  \ \_____\  \ \_____\  \ \____- 
  \/_/   \/_/   \/_____/   \/_/ /_/   \/____/   \/_____/   \/_____/   \/_____/   \/_____/   \/____/ 
@File      :   main.py
@Author    :   Fishroud鱼仙
@Contact   :   fishroud@qq.com
@Desc      :   None
'''
import OlivOS
import wordscloud

class Event(object):
    def init(plugin_event, Proc):
        pass

    def init_after(plugin_event, Proc):
        #初始化词云插件
        wordscloud.msgReply.unity_init(plugin_event, Proc)
        pass

    def group_message(plugin_event, Proc):
        wordscloud.msgReply.unity_reply(plugin_event, Proc)

    def save(plugin_event, Proc):
        wordscloud.msgReply.unity_save(plugin_event, Proc)
        pass