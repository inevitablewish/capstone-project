"""  
requirements

pip install selenium>=4.0.0.b1
pip install webdriver-manager
pip install faker

"""

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
from faker import Faker

fake_data = Faker()

website = "http://13.211.24.79:31406/"
records_to_create = int('10000')

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
driver.get(website)
print(driver.title, " Session Started")

t = 5
first_name_loc = "//input[@id='firstName']"
last_name_loc = "//input[@id='lastName']"
email_loc = "//input[@id='email']"
submit_btn_loc = "//button[@class='btn btn-default']"


for i in range(records_to_create):

    first_name = Wait(driver, t).until(EC.presence_of_element_located((By.XPATH, first_name_loc)))
    last_name = Wait(driver, t).until(EC.presence_of_element_located((By.XPATH, last_name_loc)))
    email = Wait(driver, t).until(EC.presence_of_element_located((By.XPATH, email_loc)))
    submit = Wait(driver, t).until(EC.presence_of_element_located((By.XPATH, submit_btn_loc)))

    first_name.send_keys(fake_data.first_name())
    last_name.send_keys(fake_data.last_name())
    email.send_keys(fake_data.email())
    submit.click()


driver.close()
