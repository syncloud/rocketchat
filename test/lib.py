from selenium.webdriver.common.by import By


def login_6(selenium, device_user, device_password):
    selenium.open_app()
    login = selenium.find_by(By.XPATH, "//span[.='Login with Syncloud']")
    selenium.screenshot('index')
    login.click()

    login_sso(selenium, device_user, device_password) 


def admin(selenium):
    selenium.find_by_xpath("//button[@title='Administration']").click()
    selenium.find_by_xpath("//button[@title='Workspace']")
    selenium.screenshot('admin')


def login_sso(selenium, device_user, device_password):
    selenium.find_by(By.ID, "username-textfield").send_keys(device_user)
    password = selenium.find_by(By.ID, "password-textfield")
    password.send_keys(device_password)
    selenium.screenshot('login')
    #password.send_keys(Keys.RETURN)
    selenium.find_by(By.ID, "sign-in-button").click()
    selenium.find_by(By.ID, "accept-button").click()


