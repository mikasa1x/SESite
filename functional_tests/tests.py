from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import WebDriverException
import os
import time

MAX_WAIT=10

class NewVistorTest(StaticLiveServerTestCase):

	def setUp(self):
		self.browser =  webdriver.Chrome()
		real_server = os.environ.get('REAL_SERVER')
		
		if real_server:
			self.live_server_url='http://'+real_server

	def tearDown(self):
		self.browser.quit()


	def test_layout_and_styling(self):
		self.browser.get(self.live_server_url)
		self.browser.set_window_size(1024,768)

		time.sleep(5)

		inputbox =  self.browser.find_element(By.ID,'id_new_item')

		self.assertAlmostEqual(inputbox.location['x']+inputbox.size['width']/2,
						 512,
						 delta=10
						 )
		inputbox.send_keys('testing')
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: testing')
		inputbox = self.browser.find_element(By.ID,'id_new_item')

		self.assertAlmostEqual(inputbox.location['x']+inputbox.size['width']/2,
						 512,
						 delta=10
						 )
		

	def wait_for_row_in_list_table(self,row_text):
		start_time = time.time()
		while True:
			try:
				table = self.browser.find_element(By.ID,'id_list_table')
				rows = table.find_elements(By.TAG_NAME,'tr')
				self.assertIn(row_text,[row.text for row in rows])
				return
			except (AssertionError, WebDriverException) as e:
				if time.time() - start_time > MAX_WAIT:\
					raise e
				time.sleep(0.5)



	def test_can_start_a_list_and_retrieve_it_later(self):
		self.browser.get(self.live_server_url)

		self.assertIn('To-Do',self.browser.title), "broswer title was " + self.browser.title

		header_test = self.browser.find_element(By.TAG_NAME,'h1').text

		self.assertIn('To-Do',header_test)

		inputbox = self.browser.find_element(By.ID,'id_new_item')


		self.assertEqual(inputbox.get_attribute('placeholder'),
				   
				   'Enter a to-do item')
		
		inputbox.send_keys('Buy flowers')

		inputbox.send_keys(Keys.ENTER)

		time.sleep(1)

		self.wait_for_row_in_list_table('1: Buy flowers')

		inputbox =self.browser.find_element(By.ID,'id_new_item')
		inputbox.send_keys('Give a gift to Lisi')
		inputbox.send_keys(Keys.ENTER)


		self.wait_for_row_in_list_table('1: Buy flowers')
		self.wait_for_row_in_list_table('2: Give a gift to Lisi')

		
	def test_multiple_users_can_start_lists_at_different_urls(self):
		
		# 张三新建一个待办项清单
		self.browser.get(self.live_server_url)
		inputbox = self.browser.find_element(By.ID,'id_new_item')

		inputbox.send_keys('Buy flowers')
		inputbox.send_keys(Keys.ENTER)

		self.wait_for_row_in_list_table('1: Buy flowers')

		# 张三注意到清单有一个唯一的URL
		zhangsan_list_url = self.browser.current_url 
		self.assertRegex(zhangsan_list_url,'/lists/.+')

		self.browser.quit()

		self.browser = webdriver.Chrome()

		self.browser.get(self.live_server_url)

		page_next = self.browser.find_element(By.TAG_NAME,'body').text

		self.assertNotIn('Buy flowers',page_next)
		self.assertNotIn('BGive a gift to Lisi',page_next)

		inputbox = self.browser.find_element(By.ID,'id_new_item')
		inputbox.send_keys('Buy milk')
		inputbox.send_keys(Keys.ENTER)

		self.wait_for_row_in_list_table('1: Buy milk')

		wangwu_list_url = self.browser.current_url

		self.assertRegex(wangwu_list_url,'/lists/.+')

		self.assertNotEqual(wangwu_list_url,zhangsan_list_url)

		page_next = self.browser.find_element(By.TAG_NAME,'body').text

		self.assertNotIn('Buy flowers',page_next)
		self.assertIn('Buy milk',page_next)