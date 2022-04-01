import json
from urllib import error

from numpy import true_divide
from src.utils.http_utils import RequestUtils

class Radarr:
  def __init__(self, host=None, port=None, api_key=None, is_https=False, rootFolderPath="/media/电影",qualityProfileId=1, addOptions ={},minimumAvailability= '', monitored= ''  ):
      self.req = RequestUtils(request_interval_mode=True)
      self.host = host
      self.port = port
      self.rootFolderPath = rootFolderPath
      self.qualityProfileId = qualityProfileId
      self.addOptions = addOptions
      self.minimumAvailability = minimumAvailability
      self.monitored = monitored
      self.headers={
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
      }
      self.server = '%s://%s:%s' % ("https" if is_https else "http", host, port)

  def search_all_local_movie(self):
    api = '/api/v3/movie'
    r = self.req.get(self.server + api, headers=self.headers)
    return json.loads(r)

  def exist_movie(self, imdbId):
    allMovieList = self.search_all_local_movie()
    if allMovieList is not None:
      for movie in allMovieList:
        if ('imdbId' in movie and movie['imdbId'] == imdbId):
          return True
    return False

  def search_not_exist_movie(self, search_name):
    api = '/api/v3/movie/lookup'
    r = self.req.get(self.server + api, params={'term' :search_name }, headers=self.headers)
    return json.loads(r)

  def download_movie(self, movie_info):
    api = '/api/v3/movie'
    params = movie_info
    params['qualityProfileId'] = self.qualityProfileId
    params['rootFolderPath'] = self.rootFolderPath
    params['monitored'] = self.monitored
    params['addOptions'] = self.addOptions
    params['minimumAvailability'] = self.minimumAvailability
    r = self.req.post(self.server + api, params=json.dumps(params), headers=self.headers)
    r = json.loads(r)
    if 'title' in r and r['title'] == movie_info['title']:
      print('%s 添加成功' %(movie_info['title']))
    else:
      print('%s 添加失败' %(movie_info['title']))
  def search_not_exist_movie_and_download(self, search_name, imdbId):
    search_result_list = []
    try:
      search_result_list = self.search_not_exist_movie('imdb:'+imdbId)
      if not isinstance(search_result_list, list): 
        raise Exception('请求异常')
    except Exception as e:
      search_result_list = self.search_not_exist_movie(search_name)
    if search_result_list  is not None and len(search_result_list) > 0:
      for idx,result in enumerate(search_result_list):
        if 'imdbId' in result and result['imdbId'] == imdbId:
          self.download_movie(result)
          break
        if idx >= len(search_result_list):
          print('%s 添加失败' %(search_name))
    else:
      print('%s 没有找到资源' %(search_name))

  