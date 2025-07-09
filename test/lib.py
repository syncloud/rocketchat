from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from syncloudlib.http import wait_for_rest
import requests

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


def send_message(selenium, app_domain):
    selenium.driver.get("https://{0}/channel/general".format(app_domain))
    selenium.find_by_xpath("//*[text()='Start of conversation']")
 
    selenium.find_by_xpath("//textarea[@placeholder='Message #general']").send_keys('test message')
    selenium.find_by_xpath("//textarea[@placeholder='Message #general']").send_keys(Keys.RETURN)

    selenium.screenshot('message-write')

def read_message(selenium, app_domain):
    selenium.driver.get("https://{0}/channel/general".format(app_domain))
    selenium.find_by_xpath("//*[text()='Start of conversation']")
    selenium.find_by_xpath("//div[contains(.,'test message')]")

    selenium.screenshot('message-read')


def wizard_6(selenium, app_domain, device):
    #selenium.screenshot('setup-wizard-1')
    #select = Select(selenium.find_by(By.NAME, 'Organization_Type'))
    #select.select_by_visible_text('Community')
    
    selenium.screenshot('setup-wizard-2')
    anme = selenium.find_by(By.NAME, 'organizationName')
    anme.send_keys('Syncloud')
    
    selenium.screenshot('setup-wizard-3')
    selenium.find_by(By.XPATH, "//button[@name='organizationIndustry']").click()
    selenium.find_by(By.XPATH, "//div[.='Education']").click()
    
    selenium.find_by(By.XPATH, "//button[@name='organizationSize']").click()
    selenium.find_by(By.XPATH, "//div[.='1-10 people']").click()

    selenium.find_by(By.XPATH, "//button[@name='country']").click()
    selenium.find_by(By.XPATH, "//div[.='Albania']").click()
    
    selenium.screenshot( 'setup-wizard-4-next')
    selenium.find_by(By.XPATH, '//span[.="Next"]').click()
    
    selenium.screenshot( 'setup-wizard-5-email')
    email = selenium.find_by(By.XPATH, "//input[@name='email']")
    email.send_keys('test@example.com')
    
    selenium.screenshot( 'setup-wizard-6-agreement')
    selenium.find_by(By.XPATH, "//label[contains(@class, 'rcx-check-box')]").click()
 
    selenium.screenshot( 'setup-wizard-7-register')
    selenium.find_by(By.XPATH, "//span[.='Register workspace']").click()
    
    selenium.screenshot( 'setup-wizard-7-finish')
    disable_registration_6(selenium, app_domain, device)

def wizard_7(selenium, app_domain, device):
    #selenium.screenshot('setup-wizard-1')
    #select = Select(selenium.find_by(By.NAME, 'Organization_Type'))
    #select.select_by_visible_text('Community')
    
    selenium.screenshot('setup-wizard-2')
    anme = selenium.find_by(By.NAME, 'organizationName')
    anme.send_keys('Syncloud')
    
    selenium.screenshot('setup-wizard-3')
    selenium.find_by(By.XPATH, "//label[text()='Organization industry']/..//button").click()
    selenium.find_by(By.XPATH, "//div[.='Education']").click()
    
    selenium.find_by(By.XPATH, "//label[text()='Organization size']/..//button").click()
    selenium.find_by(By.XPATH, "//div[.='1-10 people']").click()

    selenium.find_by(By.XPATH, "//label[text()='Country']/..//button").click()
    selenium.find_by(By.XPATH, "//div[.='Albania']").click()
    
    selenium.screenshot( 'setup-wizard-4-next')
    selenium.find_by(By.XPATH, '//span[.="Next"]').click()
    
    selenium.screenshot( 'setup-wizard-5-email')
    email = selenium.find_by(By.XPATH, "//input[@name='email']")
    email.send_keys('test@example.com')
    
    selenium.screenshot( 'setup-wizard-6-agreement')
    selenium.find_by(By.XPATH, "//label[contains(@class, 'rcx-check-box')]").click()
 
    selenium.screenshot( 'setup-wizard-7-register')
    selenium.find_by(By.XPATH, "//span[.='Register workspace']").click()
    
    selenium.screenshot( 'setup-wizard-7-finish')
    # disable_registration_7(selenium, app_domain, device)


def disable_registration_6(selenium, app_domain, device):
    device.run_ssh('/snap/rocketchat/current/bin/cli disable-registration')
    device.run_ssh('snap restart rocketchat.server')
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)
    selenium.open_app()

def disable_registration_7(selenium, app_domain, device):
    device.run_ssh('/snap/rocketchat/current/bin/cli disable-registration')
    #device.run_ssh('/snap/rocketchat/current/bin/mongo-disable-registration.sh')
    device.run_ssh('snap restart rocketchat.server')
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)
    selenium.open_app()
