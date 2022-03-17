
import json

from src.utils.http_utils import RequestUtils
from src.utils.movie_utils import format_serial_name
from src.utils.movie_utils import serial_name_match

class Sonarr:
  def __init__(self, host=None, port=None, api_key=None, is_https=False, rootFolderPath="/media/电影",qualityProfileId=1, languageProfileId = 2, seriesType = 'Standard',seasonFolder = True, monitored = True, addOptions = {}, typeMappingPath = [] ):
      self.req = RequestUtils(request_interval_mode=True)
      self.host = host
      self.port = port
      self.rootFolderPath = rootFolderPath
      self.qualityProfileId = qualityProfileId
      self.languageProfileId = languageProfileId
      self.seriesType = seriesType
      self.addOptions = addOptions
      self.typeMappingPath = typeMappingPath
      self.seasonFolder = seasonFolder
      self.monitored = monitored
      self.headers={
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
      }
      self.server = '%s://%s:%s' % ("https" if is_https else "http", host, port)

  def search_all_local_serial(self):
    api = '/api/v3/series'
    serial_list = self.req.get(self.server + api, headers=self.headers)
    if serial_list is not None and len(serial_list) > 0:
      return serial_list
    else:
      return None

  def download_serial(self, serial_info, douban_serial_detail):
      params = serial_info
      params['languageProfileId'] = self.languageProfileId
      params['qualityProfileId'] = self.qualityProfileId
      params['addOptions'] = self.addOptions
      params['rootFolderPath'] = self.rootFolderPath
      params['seriesType'] = self.seriesType
      params['seasonFolder'] = self.seasonFolder
      params['monitored'] = self.monitored
      cate = douban_serial_detail['cate']
      if cate is not None and len(cate) > 0:
        for c in cate:
          for t in self.typeMappingPath:
            if c in t['type']:
              params['rootFolderPath'] = t['rootFolderPath']
              params['seriesType'] = t['seriesType']
      api = '/api/v3/series'
      r = self.req.post(self.server + api, params=json.dumps(params), headers=self.headers)
      r = json.loads(r)
      if 'errorMessage' in r:
        print('添加失败: %s' %(r['errorMessage']))
      elif 'title' in r:
        print('%s 添加成功' %(r['title']))
        
      

  def search_not_exist_serial(self, search_key):
    api = '/api/v3/series/lookup'
    r = self.req.get(self.server + api, params={'term' :search_key }, headers=self.headers)
    return json.loads(r)

  def search_not_exist_serial_and_download(self, douban_serial_detail, format_all_name, original_all_name):
    search_name = douban_serial_detail['name']
    imdbId = douban_serial_detail['IMDB'].strip()
    found = False
    for idx, name in enumerate(format_all_name):
      if found: 
        return
      search_result_list = self.search_not_exist_serial(format_serial_name(name))
      if (search_result_list is not None) and (len(search_result_list) > 0):
        for result in  search_result_list:
          if ('imdbId' in result and result['imdbId'] == imdbId) or ('cleanTitle' in result and serial_name_match(result['cleanTitle'], original_all_name)):
            self.download_serial(result, douban_serial_detail)
            found = True
            break
      if (idx >= len(format_all_name) ):
        print('%s 添加失败' %(search_name))

  def exist_serial(self, imdbId, original_all_name):
    local_serial_list = self.search_all_local_serial()
    local_serial_list = json.loads(local_serial_list)
    if local_serial_list is not None:
      for serial in local_serial_list:
        if ('imdbId' in serial and serial['imdbId'] == imdbId) or ('cleanTitle' in serial and serial_name_match(serial['cleanTitle'], original_all_name) or ('title' in serial and serial['title'] in original_all_name) ) :
         return True
    return False