from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time


def login_4(selenium, device_user, device_password):
    selenium.open_app()
    selenium.screenshot('index')
    selenium.find_by_id("emailOrUsername").send_keys(device_user)
    password = selenium.find_by_id("pass")
    password.send_keys(device_password)
    selenium.screenshot('login')
    password.send_keys(Keys.RETURN)
    selenium.screenshot('login_progress')
    selenium.find_by_xpath("//button[@title='Search']")
    selenium.screenshot('main')


def login_5(selenium, device_user, device_password):
    selenium.open_app()
    selenium.screenshot('index')
    selenium.find_by(By.XPATH, "//input[@name='username']").send_keys(device_user)
    password = selenium.find_by(By.XPATH, "//input[@name='password']")
    password.send_keys(device_password)
    selenium.screenshot('login')
    password.send_keys(Keys.RETURN)
    selenium.screenshot('login_progress')
    selenium.find_by_xpath("//button[@title='Search']")
    selenium.screenshot('main')


def login_6(selenium, device_user, device_password):
    selenium.open_app()
    selenium.screenshot('index')
    selenium.find_by(By.XPATH, "//span[.='Login with Syncloud']").click()  
    selenium.find_by(By.XPATH, "//input[@name='usernameOrEmail']").send_keys(device_user)
    password = selenium.find_by(By.XPATH, "//input[@name='password']")
    password.send_keys(device_password)
    selenium.screenshot('login')
    password.send_keys(Keys.RETURN)
    selenium.screenshot('login_progress')
    selenium.find_by_xpath("//button[@title='Search']")
    selenium.screenshot('main')
    selenium.find_by_xpath("//button[@title='Administration']").click()
    selenium.find_by_xpath("//button[@title='Workspace']")
    selenium.screenshot('admin')

