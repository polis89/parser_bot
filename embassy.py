import asyncio
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import types

async def main(providedDriver = None, callbackFn = None, sendPhotoFn = None):
	print("starting embassy parser")
	if providedDriver == None:
		options = Options()
		options.add_argument("--headless")
		driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
	else:
		driver = providedDriver

	url_start = "https://appointment.bmeia.gv.at/HomeWeb"
	driver.get(url_start)
	location_select = Select(driver.find_element(By.ID, 'Office'))
	location_select.select_by_visible_text('MOSKAU')
	# location_select.select_by_visible_text('BAKU')
	driver.find_element(By.CSS_SELECTOR, ".no-border input[value='Next']").click()

	reservation_for_select = Select(driver.find_element(By.ID, 'CalendarId'))
	reservation_for_select.select_by_value('181')
	# reservation_for_select.select_by_value('5539799')
	driver.find_element(By.CSS_SELECTOR, ".no-border input[value='Next']").click()
	driver.find_element(By.CSS_SELECTOR, ".no-border input[value='Next']").click()
	driver.find_element(By.CSS_SELECTOR, "form input[value='Next']").click()

	content = driver.page_source
	soup = BeautifulSoup(content)
	error_element = soup.findAll('p',attrs={'class':'message-error'})
	if (len(error_element) == 0):
		print("NEW SLOTS IN AUSTRIAN EMBASSY")
		if isinstance(callbackFn, types.FunctionType):
			await callbackFn(["!!! IMPORTANT !!!: NEW SLOTS IN AUSTRIAN EMBASSY"], True, False)
			driver.save_screenshot('embassy_test.png')
			if isinstance(sendPhotoFn, types.FunctionType):
				await sendPhotoFn('embassy_test.png', True, False)
	else:
		print("NO SLOTS IN AUSTRIAN EMBASSY")
		# if isinstance(callbackFn, types.FunctionType):
		# 	await callbackFn(["no new slots found"], True)

	if providedDriver == None:
		driver.close()
	print("end embassy parser")

if __name__ == "__main__":
	asyncio.run(main())