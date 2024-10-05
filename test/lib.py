from selenium.webdriver.common.by import By


def login_6(selenium, device_user, device_password):
    selenium.find_by(By.XPATH, "//span[.='Login']")
    selenium.screenshot('index')

    selenium.find_by(By.XPATH, "//input[@name='usernameOrEmail']").send_keys(device_user)
    password = selenium.find_by(By.XPATH, "//input[@name='password']")
    password.send_keys(device_password)
    selenium.screenshot('login')
    password.send_keys(Keys.RETURN)
    selenium.screenshot('login_progress')


def admin(selenium):
    selenium.find_by_xpath("//button[@title='Administration']").click()
    selenium.find_by_xpath("//div[.='Workspace']")
    selenium.screenshot('admin')


def login_sso(selenium, device_user, device_password):
    selenium.find_by(By.XPATH, "//span[.='Login with Syncloud']").click()
    selenium.find_by(By.ID, "username-textfield").send_keys(device_user)
    password = selenium.find_by(By.ID, "password-textfield")
    password.send_keys(device_password)
    selenium.screenshot('login')
    selenium.find_by(By.ID, "sign-in-button").click()
    selenium.find_by(By.ID, "accept-button").click()


def send_message(selenium, app_domain):
    selenium.driver.get("https://{0}/channel/general".format(app_domain))
    selenium.find_by_xpath("//*[text()='Start of conversation']")
 
    selenium.find_by_xpath("//textarea[@placeholder='Message #general']").send_keys('test message')
    selenium.find_by_xpath("//textarea[@placeholder='Message #general']").send_keys(Keys.RETURN)


def read_message(selenium, app_domain):
    selenium.driver.get("https://{0}/channel/general".format(app_domain))
    selenium.find_by_xpath("//*[text()='Start of conversation']")
    selenium.find_by_xpath("//div[contains(.,'test message')]")

