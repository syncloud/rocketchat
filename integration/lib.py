from selenium.webdriver.common.keys import Keys


def login(selenium, device_user, device_password):
    selenium.open_app()
    selenium.screenshot('index')
    try:
        selenium.find_by_id("emailOrUsername").send_keys(device_user)
        password = selenium.find_by_id("pass")
        password.send_keys(device_password)
        selenium.screenshot('login')
        password.send_keys(Keys.RETURN)
        selenium.screenshot('login_progress')
    except Exception as e:
        print("no login required: {0}".format(str(e)))