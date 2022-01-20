import re
import cn2an
from src.utils import number_utils

__num_pattern = '[1234567890一二三四五六七八九十]+'
__episode_patterns = [
    re.compile('第(%s)[集期]' % __num_pattern),
    re.compile(r'[Ss]?(?:\d+)?[Ee][Pp]?(\d+)'),
    re.compile('第?(%s)-(%s)[集期]' % (__num_pattern, __num_pattern)),
    re.compile(r'[Ee]?[Pp]?(\d+)-[Ee]?[Pp]?(\d+)')
]
__all_episode_patterns = [
    re.compile('全(%s)[集期]' % __num_pattern), re.compile('(%s)[集期]全' % __num_pattern),
    re.compile('(?:全[集期])|(?:所有[集期])')
]
__season_patterns = [
    re.compile('第(%s)[季部辑][-—]+第(%s)[季部辑]' % (__num_pattern, __num_pattern)),
    re.compile('第(%s)[季部辑]' % __num_pattern),
    re.compile(r'[sS](\d+)'),
]
__all_season_patterns = [
    re.compile('全(%s)[季部辑]' % __num_pattern)
]
__year_patterns = re.compile('([12][0-9]{3})')
# 排除特殊年份匹配，例如清晰度
__exclude_year = ['1080', '2160']

def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

# 例如: 我们这一天 第六季 =》 我们这一天; This Is Us Season 6 => This Is Us
def format_serial_name(str = ''):
    result = str
    if is_chinese(str):
        result = str.split(' ')
    else:
        result = str.split('Season')
    if len(result) >= 2:
        return result[0].strip()
    return str
def get_Max_common_substr(s1, s2):
# 求两个字符串的最长公共子串
# 思想：建立一个二维数组，保存连续位相同与否的状态
    len_s1 = len(s1)
    len_s2 = len(s2)

    # 生成0矩阵，为方便后续计算，多加了1行1列
    # 行: (len_s1+1)
    # 列: (len_s2+1)
    record = [[0 for i in range(len_s2+1)] for j in range(len_s1+1)]    
    
    maxNum = 0          # 最长匹配长度
    p = 0               # 字符串匹配的终止下标 

    for i in range(len_s1):
        for j in range(len_s2):
            if s1[i] == s2[j]:
                # 相同则累加
                record[i+1][j+1] = record[i][j] + 1
                
                if record[i+1][j+1] > maxNum:
                    maxNum = record[i+1][j+1]
                    p = i # 匹配到下标i

    # 返回 子串长度，子串
    return maxNum, s1[p+1-maxNum : p+1]
def get_clean_title(s):
    return ''.join(list(filter(str.isalnum, s))).lower()
def serial_name_match(searched_clean_title, douban_name_list):
    for name in douban_name_list:
      [lenMatch,strMatch] =  get_Max_common_substr(searched_clean_title,get_clean_title(name))
      if (lenMatch >= len(searched_clean_title)* 0.5) :
          return True
    return False

def __to_number(str):
    if str is None:
        return None
    if str.isdigit():
        return int(str)
    else:
        try:
            return cn2an.cn2an(str)
        except ValueError as e:
            print('%s error: %s' % (str, e))
            return None


def parse_year_by_str_list(str_list=[]):
    for s in str_list:
        year = parse_year_by_str(s)
        if year is not None:
            return year
    return None


def parse_year_by_str(str):
    if str is None:
        return None
    all = re.findall(__year_patterns, str)
    year = None
    for m in all:
        if m in __exclude_year:
            continue
        else:
            year = m
            break
    return year


def parse_episode_by_name(name, total_episode):
    if name is None:
        return None
    ep_start = None
    ep_end = None
    match_all_ep = False
    # 匹配是否全集
    for p in __all_episode_patterns:
        m = p.search(name)
        if m:
            if len(m.groups()) > 0:
                end = __to_number(m.group(1))
            else:
                end = total_episode
            ep_start = 1
            ep_end = end
            match_all_ep = True
            break
    if not match_all_ep:
        for p in __episode_patterns:
            m = p.search(name)
            if m:
                if len(m.groups()) == 1:
                    ep_start = __to_number(m.group(1))
                    ep_end = None
                elif len(m.groups()) == 2:
                    ep_start = __to_number(m.group(1))
                    ep_end = __to_number(m.group(2))
                break
    has_ep = ep_start is not None or ep_end is not None
    season_start = None
    season_end = None
    match_all_season = False
    for p in __all_season_patterns:
        m = p.search(name)
        if m:
            season_start = 1
            season_end = __to_number(m.group(1))
            match_all_season = True
            break
    if not match_all_season:
        for p in __season_patterns:
            m = p.search(name)
            if m:
                if len(m.groups()) == 1:
                    season_start = __to_number(m.group(1))
                    season_end = None
                elif len(m.groups()) == 2:
                    season_start = __to_number(m.group(1))
                    season_end = __to_number(m.group(2))
                break
    auto_ep = False
    if season_start is None:
        # todo 先默认补1。应该有去查影片信息，通过含有的时间进行详细比对，确定季数
        season_start = 1
    # 匹配到独立的一季信息 并且没有任何集数信息，则大概率为整季全集
    if season_start is not None and season_end is None and not has_ep:
        ep_start = 1
        ep_end = total_episode
        match_all_ep = True
        auto_ep = True
    if season_start is not None and season_end is not None:
        # 匹配到很多季信息，集数就很难确定了
        ep_start = None
        ep_end = None
    season_index = number_utils.crate_number_list(season_start, season_end)
    ep_index = number_utils.crate_number_list(ep_start, ep_end)
    return {
        'season': {'start': season_start, 'end': season_end, 'complete': match_all_season,
                   'index': season_index},
        'ep': {'start': ep_start, 'end': ep_end, 'complete': match_all_ep, 'auto_ep': auto_ep,
               'index': ep_index, 'total_count': total_episode},
    }


if __name__ == '__main__':
    test = ['权力的游戏 2019 第八季【4K UHD 港版原盘原生中字】',
            '*活动置顶*冰与火之歌：权力的游戏 / 王座游戏 第一季-第八季 8季全集 / 【4K UHD原盘中字】',
            '权力的游戏 第八季 / Game of Thrones: The Final Season / 冰与火之歌 第八季 / 权游8 /108..',
            '权力的游戏 第八季/冰与火之歌 第八季/权游8',
            '冰与火之歌：权力的游戏 / 王座游戏 第一季-第八季 8季全集 /内封多国语言字幕',
            '权力的游戏 第八季/冰与火之歌 第八季/权游8',
            '权力的游戏 第八季 / 冰与火之歌 第八季 / 权游8',
            '权力的游戏 第八季 / 冰与火之歌 第八季 / 权游8',
            '权力的游戏 第八季 / 冰与火之歌 第八季 / 权游8',
            '冰与火之歌:权力的游戏 第八季全6集CEE版DIY简繁中字    【CEE原盘】',
            '权力的游戏 第八季 / 權力遊戲 第八季 / 冰與火之歌：權力遊戲 第八季',
            '权力的游戏 第八季（终结篇）/ 冰与火之歌 第八季/「特别添加113分钟的制作花絮」 *内封中英双语字幕',
            '【冰与火之歌：权力的游戏第八季/王座游戏 第八季】mUHD作品 4k HDR10版本',
            '权力的游戏/A Song of Ice and Fire: Game of Thrones/冰与火之歌：权力的游戏/王座游戏 第一季-第..',
            '冰与火之歌: 权力的游戏 第八季 全6集 [中英特效字幕]',
            '权力的游戏 第八季/權力遊戲 第八季/冰與火之歌：權力遊戲 第八季(Top Rated TV #8)',
            '权力的游戏 第八季 / 權力遊戲 第八季 / 冰與火之歌：權力遊戲 第八季',
            '权力的游戏 第八季 /',
            '权力的游戏 第八季/權力遊戲 第八季/冰與火之歌：權力遊戲 第八季【4K UHD重编码】',
            '[权力的游戏 第八季全6集][DiY简繁+简英繁英双语字幕]',
            '权力的游戏 第八季 CEE原盘中字 自带花絮中字',
            '权力的游戏  第八季 | 杜比视界 | 更新完毕',
            '权力的游戏 第八季 /',
            '权力的游戏 第八季',
            '权力的游戏 第八季 花絮',
            '权力的游戏 第八季 全6集 HEVC 10bit版 [内封衣柜远鉴简繁中英双语字幕] | 未删减版',
            '权力的游戏 第八季 全6集 [AMZN-GoT版本自压HEVC/H.265][保留音轨、字幕、章节等其它所有原始数据]',
            '【冰与火之歌/权力的游戏】第八季 全六集 全剧终 衣柜&人人中英字幕/简中字幕 HBO出品 HEVC版本',
            '权力的游戏 第八季 第三集/第3集/冰与火之歌/权游8 未删减含下集预告本集花絮[内封 简/繁/英/简英/繁英双语特效字幕 人人影视字幕..',
            '权力的游戏 第八季 / 权游8 第2集 [内封简繁中英双语字幕] | 未删减版 | 含幕后花絮',
            '权力的游戏 第八季 第一集/第1集/冰与火之歌/权游8 未删减含前情回顾下集预告本集花絮 [内封 简/繁/英/简英/繁英双语特效字幕 衣..',
            '权力的游戏 第八季 第六集/第6集/冰与火之歌/权游8 未删减含前情 [内封 简/繁/英/简英/繁英双语特效字幕 衣柜字幕组/远鉴字幕组..',
            '权力的游戏 第八季 / 权游8 第3集 [内封简繁中英双语字幕] | 未删减版',
            '权力的游戏 第八季 第五集/第5集/冰与火之歌/权游8 未删减含前情下集预告本集花絮[内封 简/繁/英/简英/繁英双语特效字幕 衣柜字幕..',
            '权力的游戏 第八季 第四集/第4集/冰与火之歌/权游8 未删减含前情下集预告本集花絮[内封 简/繁/英/简英/繁英双语特效字幕 衣柜字幕..',
            '权力的游戏 第八季 / 权游8 第1集 [内封简繁中英双语字幕] | 未删减版 | 含幕后花絮',
            '权力的游戏 第八季第03集 *最终季回归，Enjoy!*',
            '【冰与火之歌/权力的游戏】第八季 全六集 全剧终 衣柜&人人&官方中英字幕/简中字幕 HBO出品 HEVC版本',
            '权力的游戏 第八季 / 权游8 第4集 [内封简繁中英双语字幕] | 未删减版 | 含幕后花絮',
            '权力的游戏 第八季 / 權力遊戲 第八季 / 冰與火之歌：權力遊戲 第八季(共六集)',
            '权力的游戏 第八季 / 权游8 第5集 [内封简繁中英双语字幕] | 未删减版 | 含幕后花絮',
            '权力的游戏 第八季 / 权游8 第6集 [内封简繁中英双语字幕] | 未删减版',
            '权力的游戏 第八季 第二集/第2集/权游8',
            '权力的游戏 第八季第02集 *最终季回归，Enjoy!*',
            '权力的游戏 第八季 第二集/第2集/冰与火之歌/权游8 未删减含下集预告本集花絮[内封 简/繁/英/简英/繁英双语特效字幕 衣柜字幕组/..',
            '权力的游戏 第八季第05集 *最终季回归，Enjoy!*',
            '【权力的游戏 / 冰与火之歌：权力的游戏 / 王座游戏】第八季 六集全 全剧终 衣柜中英字幕 10bit HEVC 版本',
            '权力的游戏 第八季第01集 *最终季回归，Enjoy!*',
            '权力的游戏第八季第五集',
            '冰与火之歌: 权力的游戏 第八季 第1集',
            '权力的游戏第八季第五集',
            '权力的游戏 第八季第4集',
            '权力的游戏第八季第五集',
            '权力的游戏 第八季 第五集/第5集 未删减含前情预告花絮 单独MKV版',
            '权力的游戏 第八季/第8季 第一集/第1集 | 导演：米格尔·萨普什尼克 主演：艾米莉亚·克拉克 基特·哈灵顿 [英语英字]',
            '冰与火之歌：权力的游戏 第八季 第1集*REPACK修正版*',
            '百姓的味道 第01-06期',
            '圆桌派 第五季 第12集 | 主演：窦文涛 任长箴 刘子超 许子东',
            '圆桌派第五季全集 窦文涛/马未都/陈晓卿/尹烨/周铁君 优酷720P	']
    for s in [
        'Aladdin 2019.2160p   UHD Blu-ray HEVC TrueHD 7.1 Atmos-Thor@HDSky',
        'Jade No Poverty Land COMPLETE 1080i HDTV H264-NGB 2020'
    ]:
        print(parse_year_by_str(s), s)
    for s in ['小猪佩奇第七季.Peppa.Pig.Season.7.Complete.4K.WEB-DL.H265.AAC-OurTV']:
        data = parse_episode_by_name(s, 26)
        print(data)
        print('第%s-%s季 %s（%s-%s集 %s）    %s' % (
            data['season']['start'], data['season']['end'], '全季' if data['season']['complete'] else '未完结',
            data['ep']['start'], data['ep']['end'], '全集' if data['ep']['complete'] else '未播完', s))
