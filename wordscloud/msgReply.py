from urllib import response
import wordscloud
import wordcloud
import pathlib
import OlivOS
import jieba
import jieba.analyse
import os
import re

save_path = "./plugin/data/wordcloud/"
save_image_path = "./plugin/data/wordcloud/image/"
stop_word_path = "./plugin/data/wordcloud/stop_word.txt"

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
        tmp_log_str = '正在初始化保存文件路径'
        logProc(Proc, 2, tmp_log_str, [
            ('wordcloud', 'default'),
            ('Init', 'default')
        ])
        os.mkdir(save_path)
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

def unity_reply(plugin_event, Proc):
    global stopwords
    message = plugin_event.data.message
    command_list = deleteBlank(message)
    if len(command_list) == 1:
        if command_list[0] == 'wordcloud':
            unity_save(plugin_event, Proc)
            if plugin_event.data.host_id:
                region = str(plugin_event.data.host_id)
            else:
                region = str(plugin_event.data.group_id)
            key = 'wordcloud_' + plugin_event.platform['platform'] + '_' + region
            save_path_this = "./plugin/data/wordcloud/" + plugin_event.platform['platform'] + "/" + key + ".txt"
            if not pathlib.Path(save_path_this).exists():
                response = '该群未有词云记录'
                plugin_event.reply(response)
            else:
                with open(save_path_this, "r" ,encoding='utf-8') as f:  # 打开文件
                    words = f.read()
                w = wordcloud.WordCloud(
                    width=1000,
                    height=700,
                    background_color='white',
                    font_path="msyh.ttc"
                    )
                w.generate(words)
                w.to_file(save_image_path + key + ".png")
                image_path = os.path.abspath(save_image_path)
                image_code = '[OP:image,file=file:///' + image_path + "/" + key + ".png]"
                plugin_event.reply(image_code)
            return
    elif len(command_list) == 2:
        if command_list[0].lower() == 'reload' and command_list[1].lower() == 'stop_word':
            stopwords = [line.strip() for line in open(stop_word_path, 'r', encoding='utf-8').readlines()]
            tmp_log_str = '已重载停用词，共{}条'.format(len(stopwords))
            plugin_event.reply(tmp_log_str)
            return
        elif command_list[0].lower() == 'reload' and command_list[1].lower() == 'save':
            unity_save(plugin_event, Proc)
            return
    message = re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", message)
    message = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', "", message)
    seg_list = jieba.analyse.extract_tags(message, topK=20)
    words = '\n'.join(set(seg_list)-set(stopwords))
    words += '\n'
    glb_var = globals()
    save_key = 'wordcloud_' + plugin_event.platform['platform']
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
    tmp_log_str = '已将分词保存到全局变量{}下，由全局数组{}保存群号'.format(key,save_key)
    logProc(Proc, 2, tmp_log_str, [
        ('wordcloud', 'default'),
        ('Info', 'default')
    ])



def unity_save(plugin_event, Proc):
    glb_var = globals()
    platforms = ['qq','kaiheila','qqGuild','telegram','dodo','fanbook']
    for platform in platforms:
        save_key = 'wordcloud_' + platform
        if save_key in glb_var.keys():
            for save_this in glb_var[save_key]:
                key = save_key + "_" + save_this
                save_path_this = "./plugin/data/wordcloud/" + platform + "/"
                if not pathlib.Path(save_path_this).exists():
                    os.mkdir(save_path_this)
                save_path_this = "./plugin/data/wordcloud/" + platform + "/" + key + ".txt"
                with open(save_path_this, "a+" ,encoding='utf-8') as f:
                    f.write(glb_var[key])
                del glb_var[key]
            del glb_var[save_key]
            tmp_log_str = '已将{}平台下保存的记录写出'.format(platform)
            logProc(Proc, 2, tmp_log_str, [
                ('wordcloud', 'default'),
                ('Save', 'default')
            ])
