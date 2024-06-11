import sys
sys.path.append("D:\Anaconda2024.2\envs\test")

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10 #(1)

class NewVisitorTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True: #(2)
            try:
                table = self.browser.find_element(By.ID,'id_list_table') #(3)
                rows = table.find_elements(By.TAG_NAME,'tr')
                self.assertIn(row_text, [row.text for row in rows])
                return #(4)
            except (AssertionError, WebDriverException) as e: #(5)
                if time.time() - start_time > MAX_WAIT: #(6)
                    raise e #(6)
                time.sleep(0.5) #(5)

       

    def test_can_start_a_list_and_retrieve_it_later(self):
        # 查看应用首页
        self.browser.get(self.live_server_url)

        # 网页显示
        self.assertIn('To-Do',self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME,'h1').text #(1)
        self.assertIn('To-Do', header_text)

        # 文本输入框：待办事项
        inputbox = self.browser.find_element(By.ID, 'id_new_item') #(1)
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            "Enter a to-do item"
            )
        
        # 输入”Buy flowers“
        inputbox.send_keys('Buy flowers') #(2)

        # 回车更新，表格显示”1：Buy flowers“
        inputbox.send_keys(Keys.ENTER) #(3)
        self.wait_for_row_in_list_table('1: Buy flowers')

        # 再显示文又文本输入框：待办事项
        # 输入“Give a gift to Lisi”
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Give a gift to Lisi') 
        inputbox.send_keys(Keys.ENTER)

        #页面再次更新，清单中显示两个代办
        self.wait_for_row_in_list_table('1: Buy flowers')
        self.wait_for_row_in_list_table('2: Give a gift to Lisi')

    def test_mutiple_users_can_start_lists_at_different_urls(self):
        #zhangsan新建一个代办事项清单
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy flowers') 
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy flowers')

        #清单有唯一的url
        zhangsan_list_url = self.browser.current_url
        self.assertRegex(zhangsan_list_url, '/lists/.+') #(1)

        #新用户wangwu访问网站，开启新浏览器会话，保证cookie不泄露信息
        self.browser.quit()
        self.browser = webdriver.Chrome()

        #wangwu访问首页，但看不到张三的清单
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('Buy flowers', page_text)
        self.assertNotIn('Give a gift to Lisi', page_text)

        #wangwu输入代办，新建清单
        inputbox= self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        #王五获得唯一URL
        wangwu_list_url = self.browser.current_url
        self.assertRegex(wangwu_list_url, '/lists/.+')
        self.assertNotEqual(wangwu_list_url, zhangsan_list_url)
        
        # 这个页面还是没有张三的清单
        page_text= self.browser.find_element(By.TAG_NAME,'body').text
        self.assertNotIn('Buy flowers', page_text)
        self.assertIn('Buy milk', page_text)

        #两人都很满意，然后去睡觉了

    def test_layout_nand_styling(self):
        #张三访问网页
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024,768)#居中

        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )

        #新建清单
        inputbox.send_keys('testing')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: testing')
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )


