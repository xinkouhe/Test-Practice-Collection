# -*- coding: utf-8 -*-
"""
自动登录网易云音乐
1.引入selenium库
2.创建驱动
3.请求url
4.查找元素并点击
5.提交表单并点击
6.关闭驱动
"""
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 指明驱动路径
service = EdgeService(executable_path=r"D:\driver\edgedriver_win64\msedgedriver.exe")
options = webdriver.EdgeOptions()

# 添加启动参数，不打开浏览器页面（无头模式可能会导致iframe加载不出来）
# 伪装浏览器标识，指定本机代理转发，窗口最大化
# 禁用自动化标识（排除默认选项-启动自动化，关闭使用自动化扩展）
# options.add_argument('--headless')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0')
options.add_argument('--proxy-server=http://127.0.0.1:8888')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Edge(service=service, options=options)

driver.get('https://music.163.com')
# 拟人操作停顿
time.sleep(2)

# frame = driver.find_element(By.TAG_NAME, 'iframe')
# driver.switch_to.frame(frame)

# 两种模式，一个是主动切换到内联框架然后定位元素，推荐第二种
# 另一个是显式等待js渲染，条件是通过（）找到内联框架并切换进去
# WebDriverWait(driver, 10).until(
#     EC.frame_to_be_available_and_switch_to_it((By.ID, 'g_iframe'))
# )

# 定位登录按钮并点击，显式等待js渲染加载出按钮点击或者JS强制点击
login_link = driver.find_element(By.CSS_SELECTOR, '.m-tophead.f-pr.j-tflag a')
driver.execute_script('arguments[0].click();', login_link)
time.sleep(2)

# 选择其他登录方式
other_btn = driver.find_element(By.XPATH, '//a[contains(text(), "选择其他登录模式")]')
driver.execute_script('arguments[0].click();', other_btn)
time.sleep(2)

# 同意协议
agree_btn = driver.find_element(By.XPATH, '//*[@id="j-official-terms"]')
driver.execute_script('arguments[0].click();', agree_btn)
time.sleep(1)

# 选择账号密码登录
pss_btn = driver.find_element(By.XPATH, '//div[contains(text(), "手机号登录/注册")]')
driver.execute_script('arguments[0].click();', pss_btn)
time.sleep(3)
pwd_btn = driver.find_element(By.XPATH, '/html/body/div[7]/div/div[2]/div/div/div[2]/div[1]/a')
driver.execute_script('arguments[0].click();', pwd_btn)
time.sleep(2)

# 先找元素后send_keys()
phone_input = driver.find_element(By.XPATH, '/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[1]/div/input')
pwd_input = driver.find_element(By.XPATH, '/html/body/div[7]/div/div[2]/div/div/div[2]/section/div[2]/div/input')
phone_input.clear()
phone_input.send_keys('15298053805')
time.sleep(1)
pwd_input.clear()
pwd_input.send_keys('15298053805wyg')
time.sleep(1)

# 点击登录
login_btn = driver.find_element(By.XPATH, '/html/body/div[7]/div/div[2]/div/div/div[2]/section/a/div')
login_btn.click()

# 止步于此了，验证码检测。
# 调试
input('按回车退出...')
driver.quit()