'''
 __     __     ______     ______     _____     ______     __         ______     __  __     _____    
/\ \  _ \ \   /\  __ \   /\  == \   /\  __-.  /\  ___\   /\ \       /\  __ \   /\ \/\ \   /\  __-.  
\ \ \/ ".\ \  \ \ \/\ \  \ \  __<   \ \ \/\ \ \ \ \____  \ \ \____  \ \ \/\ \  \ \ \_\ \  \ \ \/\ \ 
 \ \__/".~\_\  \ \_____\  \ \_\ \_\  \ \____-  \ \_____\  \ \_____\  \ \_____\  \ \_____\  \ \____- 
  \/_/   \/_/   \/_____/   \/_/ /_/   \/____/   \/_____/   \/_____/   \/_____/   \/_____/   \/____/ 
@File      :   msgReply.py
@Author    :   Fishroud鱼仙
@Contact   :   fishroud@qq.com
@Desc      :   None
'''

import wordscloud
import wordcloud
import pathlib
import OlivOS
import jieba
import jieba.analyse
import os
import re

platforms = ['qq','kaiheila','qqGuild','telegram','dodo','fanbook']
save_path = "./plugin/data/wordcloud/"
save_admin_path = save_path + "admin/"
save_image_path = save_path + "image/"
stop_word_path = save_path + "stop_word.txt"
stop_uid_path = save_path + "stop_uid/"

def logProc(Proc, level, message, segment):
    Proc.log(
        log_level = level,
        log_message = message,
        log_segment = segment
    )

def deleteBlank(str):
    str_list = list(filter(None,str.split(" ")))
    return str_list

def unity_init(plugin_event, Proc):
    #初始化词云插件
    #初始化保存路径
    global stopwords
    if not pathlib.Path(save_path).exists():
        os.mkdir(save_path)
    if not pathlib.Path(save_admin_path).exists():
        os.mkdir(save_admin_path)
    for platform in platforms:
        #初始化分词保存文件
        save_path_this = save_path + platform + '/'
        if not pathlib.Path(save_path_this).exists():
            os.mkdir(save_path_this)
            tmp_log_str = '已初始化{}平台保存文件路径'.format(platform)
            logProc(Proc, 2, tmp_log_str, [
                ('wordcloud', 'default'),
                ('Init', 'default')
            ])
    #初始化管理文件
    load_admin(Proc)
    if not pathlib.Path(save_image_path).exists():
        tmp_log_str = '正在初始化图片保存文件路径'
        logProc(Proc, 2, tmp_log_str, [
            ('wordcloud', 'default'),
            ('Init', 'default')
        ])
        os.mkdir(save_image_path)
    tmp_log_str = '正在检查停用词文件'
    logProc(Proc, 2, tmp_log_str, [
            ('wordcloud', 'default'),
            ('Init', 'default')
        ])
    #初始化停用词列表
    load_stop_word(Proc)
    #初始化过滤名单
    if not pathlib.Path(stop_uid_path).exists():
            os.mkdir(stop_uid_path)
    load_stop_uid(Proc)



def unity_reply(plugin_event, Proc):
    global stopwords
    glb_var = globals()
    message = plugin_event.data.message
    command_list = deleteBlank(message)
    #过滤屏蔽用户
    uid = plugin_event.data.user_id
    platform = plugin_event.platform['platform']
    if is_stop_uid(uid ,platform):
        tmp_log_str = '收到来自用户{}的消息，但已被过滤'.format(uid)
        logProc(Proc, 2, tmp_log_str, [
            ('wordcloud', 'default'),
            ('Info', 'default')
        ])
        return
    if len(command_list) == 1:
        if command_list[0].lower() == 'wordcloud':
            response = '正在尝试生成本群词云......'
            plugin_event.reply(response)
            #unity_save(plugin_event, Proc)
            if plugin_event.data.host_id:
                region = str(plugin_event.data.host_id)
            else:
                region = str(plugin_event.data.group_id)
            key = 'wordcloud_' + platform + '_' + region
            save_path_this = save_path + platform + "/" + key + ".txt"
            save_key = 'wordcloud_' + platform
            if key in glb_var.keys():
                with open(save_path_this, "a+" ,encoding='utf-8') as f:
                    f.write(glb_var[key])
                glb_var[save_key].remove(region)
                del glb_var[key]
            if not pathlib.Path(save_path_this).exists():
                response = '该群未有词云记录'
                plugin_event.reply(response)
            else:
                with open(save_path_this, "r" ,encoding='utf-8') as f:  # 打开文件
                    words = f.read()
                w = wordcloud.WordCloud(
                    width = 1000,
                    height = 700,
                    background_color = 'white',
                    collocations = False,
                    font_path = "msyh.ttc"
                    )
                w.generate(words)
                w.to_file(save_image_path + key + ".png")
                image_path = os.path.abspath(save_image_path)
                image_code = '[OP:image,file=file:///' + image_path + "/" + key + ".png]"
                plugin_event.reply(image_code)
            return
    elif len(command_list) == 2:
        if command_list[0].lower() == 'wordcloud' and command_list[1].lower() == '-v':
            response = 'WordsCloud Plugin by Fishroud\n'
            response += 'Powered by OlivOS jieba wordcloud'
            plugin_event.reply(response)
            return
        if command_list[0].lower() == 'wordcloud' and command_list[1].lower() == 'reload' and is_admin(uid ,platform):
            unity_save(Proc)
            load_admin(Proc)
            load_stop_word(Proc)
            load_stop_uid(Proc)
            response = '重载操作已完成'
            plugin_event.reply(response)
            return
    message = re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", message)
    message = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', "", message)
    seg_list = jieba.analyse.extract_tags(message, topK=20)
    words = '\n'.join(set(seg_list)-set(stopwords))
    words += '\n'
    glb_var = globals()
    save_key = 'wordcloud_' + platform
    if plugin_event.data.host_id:
        region = str(plugin_event.data.host_id)
    else:
        region = str(plugin_event.data.group_id)
    key = save_key + '_' + region
    if key in glb_var.keys():
        glb_var[key] += words
    else:
        glb_var[key] = words
    if save_key in glb_var.keys():
        if not region in glb_var[save_key]:
            glb_var[save_key].append(region)
    else:
        glb_var[save_key] = []
        glb_var[save_key].append(region)



def unity_save(Proc):
    glb_var = globals()
    for platform in platforms:
        save_key = 'wordcloud_' + platform
        if save_key in glb_var.keys() and len(glb_var[save_key]) > 0:
            for save_this in glb_var[save_key]:
                key = save_key + "_" + save_this
                save_path_this = save_path + platform + "/"
                if not pathlib.Path(save_path_this).exists():
                    os.mkdir(save_path_this)
                save_path_this = save_path + platform + "/" + key + ".txt"
                with open(save_path_this, "a+" ,encoding='utf-8') as f:
                    f.write(glb_var[key])
                del glb_var[key]
            del glb_var[save_key]
            tmp_log_str = '已将{}平台下保存的记录写出'.format(platform)
            logProc(Proc, 2, tmp_log_str, [
                ('wordcloud', 'default'),
                ('Save', 'default')
            ])


def load_admin(Proc):
    glb_var = globals()
    for platform in platforms:
        key = platform + '_admin'
        save_admin_path_this = save_admin_path + key + '.txt'
        if not pathlib.Path(save_admin_path_this).exists():
            f = open(save_admin_path_this, 'w', encoding='utf-8')
            f.close()
            tmp_log_str = '已初始化{}平台管理文件{}'.format(platform,key + '.txt')
            logProc(Proc, 2, tmp_log_str, [
                ('wordcloud', 'default'),
                ('Init', 'default')
            ])
        glb_var[key] = [line.strip() for line in open(save_admin_path_this, 'r', encoding='utf-8').readlines()]
        uid_num = len(glb_var[key])
        if uid_num > 0:
            tmp_log_str = '已加载{}管理名单{}条'.format(platform,uid_num)
            logProc(Proc, 2, tmp_log_str, [
                ('wordcloud', 'default'),
                ('Init', 'default')
            ])
    return

def load_stop_word(Proc):
    global stopwords
    if not pathlib.Path(stop_word_path).exists():
        tmp_log_str = '默认停用词不存在，正在自动写出'
        logProc(Proc, 2, tmp_log_str, [
            ('wordcloud', 'default'),
            ('Init', 'default')
        ])
        with open(stop_word_path,"w" ,encoding='utf-8') as f:
            f.write(wordscloud.data.stop_word)
    stopwords = [line.strip() for line in open(stop_word_path, 'r', encoding='utf-8').readlines()]
    tmp_log_str = '已加载停用词{}条'.format(len(stopwords))
    logProc(Proc, 2, tmp_log_str, [
        ('wordcloud', 'default'),
        ('Init', 'default')
    ])
    return

def load_stop_uid(Proc):
    glb_var = globals()
    for platform in platforms:
        stop_uid_path_this = stop_uid_path + platform + '/'
        if not pathlib.Path(stop_uid_path_this).exists():
            os.mkdir(stop_uid_path_this)
        stop_uid_file_path_this = stop_uid_path_this + 'stop.txt'
        key = 'stop_uid_' + platform
        if not pathlib.Path(stop_uid_file_path_this).exists():
            f = open(stop_uid_file_path_this, 'w', encoding='utf-8')
            f.close()
        glb_var[key] = [line.strip() for line in open(stop_uid_file_path_this, 'r', encoding='utf-8').readlines()]
        uid_num = len(glb_var[key])
        if uid_num > 0:
            tmp_log_str = '已加载{}屏蔽名单{}条'.format(platform,uid_num)
            logProc(Proc, 2, tmp_log_str, [
                ('wordcloud', 'default'),
                ('Init', 'default')
            ])

def is_admin(uid ,platform):
    glb_var = globals()
    admin_uid_list = glb_var[platform + '_admin']
    #admin用户
    if str(uid) in admin_uid_list:
        return True
    else:
        return False

def is_stop_uid(uid ,platform):
    glb_var = globals()
    stop_uid_list = glb_var['stop_uid_' + platform]
    #过滤屏蔽用户
    if str(uid) in stop_uid_list:
        return True
    else:
        return False