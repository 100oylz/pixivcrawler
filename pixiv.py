import json
import os
import random
import time

import requests
from fake_useragent import UserAgent


class pixivxpider():
	def __init__(self):
		self.infourl = 'https://www.pixiv.net/ajax/illust/'  # 利用join加入id
		self.imgurllist = 'https://www.pixiv.net/ajax/illust///pages?lang=zh'  # 利用replace替换中间//
		self.searchurl = 'https://www.pixiv.net/ajax/search/artworks/'
		self.rankurl = 'https://www.pixiv.net/ranking.php'
		self.count = 0
		self.is_rank = 0
		self.headers = {
			'user-agent': UserAgent().random,
			'referer': 'https://www.pixiv.net'
		}
		self.max = 0
	
	def mode(self):
		self.count=0
		print("请选择模式：")
		print("输入0：搜索")
		print("输入1：排行榜")
		print("输入2：退出")
		self.is_rank = int(input("请输入0或1或2："))
		
		if (self.is_rank == 0):
			self.search()
			self.mode()
		# self.mode()
		elif (self.is_rank == 1):
			self.rank()
			self.mode()
		elif (self.is_rank == 2):
			self.exit()
		else:
			print("输入错误")
			self.mode()
	
	def imginfo(self, id=''):
		if (id == ''):
			pass
		else:
			try:
				print('')
				info_response = requests.get(url=self.infourl + id, headers=self.headers, timeout=5)
			except Exception as e:
				print(e)
				print('获取详情失败')
				return 0
			else:
				info_result = json.loads(info_response.text)
				like_count = info_result['body']['likeCount']
				view_count = info_result['body']['viewCount']
				bookmark_count = info_result['body']['bookmarkCount']
				urls = []
				try:
					img_url = self.imgurllist.replace('///', '/{}/'.format(id))
					img_response = requests.get(url=img_url, headers=self.headers, timeout=5)
				
				except:
					print("图片url获取失败")
				else:
					url_list = json.loads(img_response.text)['body']
					for url in url_list:
						urls.append(url['urls']['original'])
				return like_count, bookmark_count, view_count, urls
	
	def search(self):
		name = input("请输入关键词：")
		searchurl = self.searchurl + name
		select = int(input("请输入想要查看的最低赞数："))
		self.max = int(input("请输入爬取的图片数量："))
		img_info = {}
		self.makedir(name)
		page = 1
		while (1):
			params = {'p': str(page), 's_mode': 's_tag'}
			search_response = requests.get(url=searchurl, headers=self.headers)
			search_result = json.loads(search_response.text)
			Data = search_result['body']['illustManga']['data']
			
			print('本次检索到了{}条数据'.format(len(Data)))
			for data in Data:
				try:
					ID = data['id']
					print(ID)
					title = data['title']
					imgtype = data['illustType']
					information = self.imginfo(ID)
					# print(information)
				
					if (int(information[1]) >= select and imgtype == '0'):
						img_info[title] = [ID, imgtype, information]
						num = 0
						for imgurl in information[3]:
							self.download(url=imgurl, title=title, name=name, num=num)
							num += 1
							self.count += 1
							print(self.count)
					else:
						print("赞数过低，跳过")
					time.sleep(random.uniform(1, 3))
					if (self.count >= self.max):
						print("成功爬取了{}个图片".format(self.count))
						break
				except:
					print("获取图片信息出错")
			page+=1
		print(img_info)
		return 0
	
	def rank(self):
		
		localtime = time.localtime()
		name = f'{localtime.tm_year}-{localtime.tm_mon}-{localtime.tm_mday}排行榜'
		self.makedir(name=name)
		params = {'mode': 'daily',
		          'format': 'json',
		          'content': 'illust'}
		rank_response = requests.get(url=self.rankurl, headers=self.headers, params=params)
		rank_result = json.loads(rank_response.text)
		# print(rank_result)
		Data = rank_result['contents']
		img_info = {}
		print('本次检索到了{}条数据'.format(len(Data)))
		for data in Data:
			try:
				ID = str(data['illust_id'])
				print(ID)
				title = data['title']
				imgtype = data['illust_type']
				information = self.imginfo(ID)
				img_info[title] = [ID, imgtype, information]
				num = 0
				for imgurl in information[3]:
					self.download(url=imgurl, title=title, name=name, num=num)
					num += 1
					self.count += 1
					print(self.count)
					time.sleep(random.uniform(1, 3))
			except:
				print("获取详情失败")
		return 0
	
	def exit(self):
		print("*" * 20)
		print("您本次的pixiv旅程到此结束")
		print("下次再见")
		print("*" * 20)
		return 0
	
	def makedir(self, name):
		if not os.path.exists('pixiv爬虫'):
			os.mkdir('pixiv爬虫')
			print('创建文件夹成功')
		else:
			print("路径已存在")
		if not os.path.exists('pixiv爬虫/{}'.format(name)):
			os.mkdir('pixiv爬虫/{}'.format(name))
			print('创建文件夹成功')
		else:
			print("路径已存在")
	
	def download(self, url, title, name, num=0):
		print('请等待下载，等待时间可能很长~~~~~~:')
		try:
			img_response = requests.get(url=url, headers=self.headers, timeout=5)
		except:
			print("获取图片失败")
		else:
			houzhui = url.split('.')[-1]
			with open(f'pixiv爬虫/{name}/{title}+{str(num)}.{houzhui}', 'wb') as fp:
				fp.write(img_response.content)
			print("获取图片成功")


if __name__ == '__main__':
	spider = pixivxpider()
	spider.mode()
