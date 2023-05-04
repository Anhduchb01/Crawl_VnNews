import scrapy
from vn_news.items import ReportItem
import urllib
import os
class BaoCaoCafefSpider(scrapy.Spider):
	name = "baocaocafef"
	start_urls = ['http://s.cafef.vn/phan-tich-bao-cao.chn']
	download_dir = 'downloads/'
	i  = 0
	def parse(self, response):
		list_id_item = []
		for index in range(20):
			if index % 2 == 0:
				id_item = "#ContentPlaceHolder1_AnalyzeReportList1_rptData_itemTR_"+str(index)
			else:
				id_item = "#ContentPlaceHolder1_AnalyzeReportList1_rptData_altitemTR_"+str(index)
			print(id_item)
			list_id_item.append(id_item)    
			date = response.css(id_item+' > td.Item_DateItem::text').get()
			date= self.formatString(date)
			title = response.css(id_item+' > td:nth-child(2) > a::text').get()
			title= self.formatString(title)
			print(title)
			source = response.css(id_item+'> td:nth-child(3)::text').get()
			source= self.formatString(source)
			number_CK = response.css(id_item+'> td:nth-child(4)::text').get()
			number_CK= self.formatString(number_CK)
			try:
				id_pdf = response.css(id_item+' > td:nth-child(5) > a::attr(onclick)').get()
				id_pdf = id_pdf.split(",")[1].strip("'")
			except:
				id_pdf=""
			os.makedirs(self.download_dir, exist_ok=True)
			if id_pdf != "":
				pdf_url = f'https://cafef1.mediacdn.vn/Images/Uploaded/DuLieuDownload/PhanTichBaoCao/{id_pdf}'
				print('Download :',id_pdf)
				# download the PDF file
				filepath = self.download_dir + id_pdf
				urllib.request.urlretrieve(pdf_url, filepath)
			value_selected_page = response.xpath('//table[contains(@class, "CafeF_Paging")]//input[@class="btn_Search_Selected"]//@value').get()
			item = ReportItem(
				page = str(value_selected_page),
				id_item =id_item, 
				date = date,
				title=title,
				source=source,
				number_CK=number_CK,
				id_pdf=id_pdf
			)
			
			yield item
		value_selected_page = response.xpath('//table[contains(@class, "CafeF_Paging")]//input[@class="btn_Search_Selected"]//@value').get()
	
		next_value = int(value_selected_page)+1
		name_next_page = response.xpath('//table[contains(@class, "CafeF_Paging")]//input[@value="'+str(next_value)+'"]//@name').get()
		if name_next_page and name_next_page is not None:
			if int(next_value) <=5:
				yield scrapy.FormRequest.from_response(
					response,
					formdata={name_next_page: str(next_value)},
					callback=self.parse,
					clickdata={'name': name_next_page},
					dont_filter=True
				)
	def formatString(self, text):
		text= text.strip()
		text = text.replace('\r\n','') 
		text = text.replace('\r','') 
		text = text.replace('\n','') 
		text =  text.replace('"', '')
		text = text.replace("'", "") 

		return text
	def save_pdf(self, response):
		file_name = response.meta['file_name']
		with open(file_name, 'wb') as f:
			f.write(response.body)
		self.log(f'Saved file {file_name}')