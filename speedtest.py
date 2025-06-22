from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# ChromeDriverのパス（例: Windowsなら 'C:\\path\\to\\chromedriver.exe'）
chromedriver_path = ''  # ← 自分の環境に合わせて変更

# オプション設定（ヘッドレスにはしない）
options = Options()
# options.add_argument('--headless')  # ← これは使わない

while True:
	# Chromeブラウザを起動
	service = Service(executable_path=chromedriver_path)
	driver = webdriver.Chrome(service=service, options=options)

	# 対象サイトへアクセス
	driver.get("http://www.speed-visualizer.jp/")

	try:
		wait = WebDriverWait(driver, 15)

		# 都道府県「一覧から選ぶ」→ 北海道
		wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-location[data-target="#modalPrefectures"]'))).click()
		wait.until(EC.visibility_of_element_located((By.ID, 'modalPrefectures')))
		time.sleep(1.5)
		driver.execute_script("arguments[0].click();",
			wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="prefectures"][value="北海道"]'))))

		# サービス「NTT東日本」
		driver.execute_script("arguments[0].click();",
			wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="service"][value="NTT東日本（コラボ光含む）"]'))))

		# ISP「一覧から選ぶ」→ SoftBank 光
		wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-isp[data-target="#modalIsp"]'))).click()
		wait.until(EC.visibility_of_element_located((By.ID, 'modalIsp')))
		time.sleep(1.5)
		driver.execute_script("arguments[0].click();",
			wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="isp"][value="SoftBank 光"]'))))

		# 住居「マンション」
		driver.execute_script("arguments[0].click();",
			wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="environment"][value="マンション"]'))))

		# ネットワーク「有線（LANケーブル）」
		driver.execute_script("arguments[0].click();",
			wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="network"][value="有線（LANケーブル）"]'))))

		# 利用規約を表示ボタンをクリック
		terms_button = wait.until(EC.element_to_be_clickable((By.ID, 'termsButton')))
		driver.execute_script("arguments[0].click();", terms_button)
		print("利用規約ボタンをクリック")

		# 1秒待機（モーダルが開くのを待つ）
		time.sleep(1.0)

		# 「×閉じる」ボタンを強制クリック（クリック可能かどうか確認せず実行）
		try:
			close_button = driver.find_element(By.XPATH, '/html/body/main/div[1]/section[7]/div[2]/div/div/div[1]/div/button')
			driver.execute_script("arguments[0].click();", close_button)
			print("XPathで取得したbtn-closeをクリックしました")
		except Exception as e:
			print("閉じる画像のクリックに失敗:", e)

		# 同意チェックをON
		agree_checkbox = wait.until(EC.presence_of_element_located((By.ID, 'agreementCheck')))
		if not agree_checkbox.is_selected():
			driver.execute_script("arguments[0].click();", agree_checkbox)

		# ✅ 測定開始ボタンをクリック ← NEW!!
		start_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-action')))
		start_button.click()
		print("測定開始ボタンをクリックしました")

		# ▼ 測定完了まで十分に待機（※30秒以上かかる場合も）
		time.sleep(20)  # 必要に応じて調整

		# ▼ 測定結果を取得（XPathからテキストを抜き出し）
		try:
			ipv4_download = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/section[1]/table/tbody/tr[2]/td[2]/span').text
			ipv4_upload   = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/section[1]/table/tbody/tr[2]/td[3]/span').text
			ipv6_download = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/section[1]/table/tbody/tr[3]/td[2]/span').text
			ipv6_upload   = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/section[1]/table/tbody/tr[3]/td[3]/span').text

			print("測定結果を取得しました")
			print(f"IPv4 DL: {ipv4_download}, UL: {ipv4_upload}")
			print(f"IPv6 DL: {ipv6_download}, UL: {ipv6_upload}")

		except Exception as e:
			print("測定結果の取得に失敗しました:", e)

		

		# 追加のボタンをクリック
		extra_button = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/section[2]/button')
		driver.execute_script("arguments[0].click();", extra_button)
		print("指定されたボタン（/html/body/...）をクリックしました")
		
		time.sleep(2)

		try:
			ipv6_dl_internal = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[3]/section[1]/table/tbody/tr[3]/td[2]/span').text
			ipv6_ul_internal = driver.find_element(By.XPATH, '/html/body/main/div[2]/div[3]/section[1]/table/tbody/tr[3]/td[3]/span').text

			print("IPv6インターナル測定結果を取得しました")
			print(f"DL: {ipv6_dl_internal}, UL: {ipv6_ul_internal}")

			# ▼ CSV形式で追記保存
			with open("result.txt", "a", newline='', encoding="utf-8") as f:
				writer = csv.writer(f)
				# writer.writerow([
				# 		"測定日時",
				#         "IPv4ダウンロード", "IPv4アップロード",
				#         "IPv6ダウンロード", "IPv6アップロード",
				#         "IPv6ダウンロード(インターナル)", "IPv6アップロード(インターナル)"
				# ])
				writer.writerow([
						time.strftime("%Y-%m-%d %H:%M:%S"),
						ipv4_download, ipv4_upload,
						ipv6_download, ipv6_upload,
						ipv6_dl_internal, ipv6_ul_internal
				])



		except Exception as e:
			print("インターナル結果の取得に失敗しました:", e) 
		


	finally:
		driver.quit()  # 終了後に自動で閉じたい場合
		time.sleep(600)	  # 10分待機（次の測定までのインターバル）
		pass
