
from src.movie.douban import DoubanMovie
from src.radarr.utils import Radarr
from src.sonarr.utils import Sonarr
from src.utils.movie_utils import format_serial_name


class Downloader:
    def __init__(self, **kwargs):
        self.workdir = kwargs['workdir']
        self.douban_config = kwargs['douban']
        self.douban = DoubanMovie()
        self.radarr= Radarr(
            host=kwargs['radarr']['host'],
            port=kwargs['radarr']['port'],
            api_key=kwargs['radarr']['api_key'],
            is_https=kwargs['radarr']['https'],
            rootFolderPath=  kwargs['radarr']['rootFolderPath'],
            qualityProfileId= kwargs['radarr']['qualityProfileId'],
            addOptions = kwargs['radarr']['addOptions'],
            minimumAvailability = kwargs['radarr']['minimumAvailability'],
            monitored = kwargs['radarr']['monitored']
        )
        self.sonarr = Sonarr( 
            host=kwargs['sonarr']['host'],
            port=kwargs['sonarr']['port'],
            api_key=kwargs['sonarr']['api_key'],
            is_https=kwargs['sonarr']['https'],
            rootFolderPath=  kwargs['sonarr']['rootFolderPath'],
            qualityProfileId= kwargs['sonarr']['qualityProfileId'],
            languageProfileId = kwargs['sonarr']['languageProfileId'],
            seriesType = kwargs['sonarr']['seriesType'],
            seasonFolder = kwargs['sonarr']['seasonFolder'],
            monitored = kwargs['sonarr']['monitored'],
            addOptions = kwargs['sonarr']['addOptions'],
            typeMappingPath = kwargs['sonarr']['typeMappingPath'],
        )
    def start(self):
        users = self.douban_config['user_domain']
        for u in users:
            self.search_and_download(
                u,
                types=self.douban_config['types'],
                within_days=self.douban_config['within_days'],
                turn_page=self.douban_config['turn_page']
            )
        print('所有用户的影视下载已经完成。')


    def search_and_download(self, douban_user, types=['wish'], within_days=365, turn_page=True):
        movie_list = self.douban.get_user_movie_list(douban_user, types=types, within_days=within_days,
                                                     turn_page=turn_page)
        if movie_list is None:
            print('%s没有任何影视资源需要下载' % douban_user)
            return None
        print('已经获得%s的全部影视，共有%s个需要智能检索' % (douban_user, len(movie_list)))
        for douban_list_item in movie_list:
            movie_detail = self.douban.get_movie_by_id(douban_list_item['id'])
            if movie_detail is None:
                print('%s(id:%s)信息获取异常' % (douban_list_item['name'], douban_list_item['id']))
                continue
            type = movie_detail['type']
            imdb = movie_detail['IMDB'].strip()
            local_name = movie_detail['local_name']
            alias = movie_detail['alias']
            search_name = douban_list_item['name']
            is_series = 'Series' == type
            if is_series:
               original_all_name = [search_name, local_name]
               original_all_name.extend(alias)
               format_all_name = []
               for name in original_all_name:
                   format_all_name.append(format_serial_name(name)) 
               format_all_name = list(set(format_all_name))
               exist = self.sonarr.exist_serial(imdb, original_all_name)
               if exist:
                   print('剧集%s已经存在，跳过下载' %(search_name))
               else:
                    print('尝试添加%s' %(search_name))
                    self.sonarr.search_not_exist_serial_and_download(movie_detail, format_all_name, original_all_name)
            else:
               exist = self.radarr.exist_movie(imdb)
               if exist:
                   print('电影%s已经存在，跳过下载' %(search_name))
               else:
                    print('尝试添加%s' %(search_name))
                    self.radarr.search_not_exist_movie_and_download(search_name, imdb)
