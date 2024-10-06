from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def login_6(selenium, device_user, device_password):
    selenium.find_by(By.XPATH, "//span[.='Login']")
    selenium.screenshot('index')

    selenium.find_by(By.XPATH, "//input[@name='usernameOrEmail']").send_keys(device_user)
    password = selenium.find_by(By.XPATH, "//input[@name='password']")
    selenium.screenshot('login-6')
    password.send_keys(device_password)
    password.send_keys(Keys.RETURN)
    selenium.screenshot('login-6-progress')
    selenium.find_by_xpath("//button[@title='User menu']")
    selenium.screenshot('login-6-done')


def admin(selenium):
    selenium.find_by_xpath("//button[@title='Administration']").click()
    selenium.find_by_xpath("//div[.='Workspace']").click()
    selenium.find_by_xpath("//h1[.='Workspace']")
    selenium.screenshot('admin')
    selenium.find_by_xpath("//button[@aria-label='Close']").click()


def login_sso(selenium, device_user, device_password):
    login = selenium.find_by(By.XPATH, "//span[.='Login with Syncloud']")
    selenium.screenshot('login-sso')
    login.click()
    selenium.find_by(By.ID, "username-textfield").send_keys(device_user)
    password = selenium.find_by(By.ID, "password-textfield")
    password.send_keys(device_password)
    selenium.find_by(By.ID, "sign-in-button").click()
    selenium.screenshot('login-sso-accept')
    selenium.find_by(By.ID, "accept-button").click()
    selenium.find_by(By.XPATH, "//div[.='Organization Info']").
    #selenium.find_by_xpath("//button[@title='User menu']")
    selenium.screenshot('login-sso-done')

def send_message(selenium, app_domain):
    selenium.driver.get("https://{0}/channel/general".format(app_domain))
    selenium.find_by_xpath("//*[text()='Start of conversation']")
 
    selenium.find_by_xpath("//textarea[@placeholder='Message #general']").send_keys('test message')
    selenium.find_by_xpath("//textarea[@placeholder='Message #general']").send_keys(Keys.RETURN)


def read_message(selenium, app_domain):
    selenium.driver.get("https://{0}/channel/general".format(app_domain))
    selenium.find_by_xpath("//*[text()='Start of conversation']")
    selenium.find_by_xpath("//div[contains(.,'test message')]")
