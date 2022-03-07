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