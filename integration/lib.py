from selenium.webdriver.common.keys import Keys


def login_3(selenium, device_user, device_password):
    selenium.open_app()
    selenium.screenshot('index')
    selenium.find_by_id("emailOrUsername").send_keys(device_user)
    password = selenium.find_by_id("pass")
    password.send_keys(device_password)
    selenium.screenshot('login')
    password.send_keys(Keys.RETURN)
    selenium.screenshot('login_progress')
    #v4 selenium.find_by_xpath("//button[@title='Search']")
    selenium.find_by_xpath("//button[@data-qa='sidebar-search']")
    selenium.screenshot('main')


def login_2(selenium, device_user, device_password):
    selenium.open_app()
    selenium.screenshot('index')
    selenium.find_by_id("emailOrUsername").send_keys(device_user)
    password = selenium.find_by_id("pass")
    password.send_keys(device_password)
    selenium.screenshot('login')
    password.send_keys(Keys.RETURN)
    selenium.screenshot('login_progress')
    #v4 selenium.find_by_xpath("//button[@title='Search']")
    selenium.find_by_xpath("//button[@aria-label='Search']")
    selenium.screenshot('main')


