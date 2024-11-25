import random
import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
from colorama import init, Fore, Back, Style

# Inisialisasi colorama
init(autoreset=True)

# Daftar beberapa User-Agent yang dapat digunakan untuk menghindari pemblokiran
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:56.0) Gecko/20100101 Firefox/56.0'
]

# Blacklist domain yang tidak boleh disimpan
BLACKLIST_DOMAINS = [
    'docs.leakix.net',
    'blog.leakix.net',
    'infosec.exchange',
    'twitter.com',
    'linkedin.com',
    'github.com'
]

# Fungsi untuk mengecek apakah domain ada dalam blacklist
def is_blacklisted(url):
    domain = urlparse(url).netloc
    for blacklisted_domain in BLACKLIST_DOMAINS:
        if blacklisted_domain in domain:
            return True
    return False

# Fungsi untuk menangani Ban (IP diblokir)
def handle_ban():
    print(Fore.RED + "Your IP may be banned. Please consider changing your IP address.")
    time.sleep(30)  # Tunggu 1 menit atau lebih sebelum mencoba lagi

# Fungsi untuk mendapatkan URL dari halaman pencarian menggunakan Selenium
def get_urls_from_page(page_number, keyword, country, driver, existing_urls):
    base_url = f"https://leakix.net/search?page={page_number}&q={keyword}+%2Bcountry%3A%22{country}%22&scope=leak"
    
    # Menggunakan Selenium untuk memuat halaman
    driver.get(base_url)
    
    # Tunggu beberapa detik agar halaman sepenuhnya dimuat
    time.sleep(2)  # Sesuaikan dengan kecepatan halaman
    
    # Ambil source halaman untuk analisis lebih lanjut
    pg = driver.page_source
    
    # Penanganan jika ada CAPTCHA atau pembatasan
    if "DDoS protection" in pg:
        print(Fore.YELLOW + "Captcha detected! Please solve it manually.")
        input(Fore.YELLOW + "Press Enter after solving the captcha manually in the browser.")
    elif "Your request is rate limited" in pg:
        print(Fore.YELLOW + "Rate limit reached, sleeping for 7 seconds...")
        time.sleep(7)  # Tunggu sebelum mencoba lagi
    elif "The request site is currently unavailable" in pg:
        handle_ban()  # Tangani ban (IP change diperlukan)
    
    # Temukan semua link hasil pencarian di dalam halaman
    links = driver.find_elements(By.XPATH, "//a[starts-with(@href, 'http')]")
    
    # Ambil hanya URL yang relevan
    urls = [link.get_attribute('href') for link in links]
    
    # Debugging: Menampilkan jumlah URL yang ditemukan pada halaman
    for url in urls:
        if url not in existing_urls and not is_blacklisted(url):
            print(Fore.CYAN + f"{url}\n")
    
    return urls

# Fungsi untuk menyimpan URL ke file tanpa duplikat
def save_urls_to_file(urls, filename):
    existing_urls = set()
    
    # Baca URL yang sudah ada di file dan pastikan tidak ada duplikasi
    try:
        with open(filename, 'r') as file:
            existing_urls = set(file.read().splitlines())
    except FileNotFoundError:
        # Jika file tidak ada, kita buat file baru
        pass
    
    # Tulis URL baru yang belum ada di file dan tidak berasal dari blacklist
    with open(filename, 'a') as file:
        for url in urls:
            if url not in existing_urls and not is_blacklisted(url):
                file.write(url + '\n')
                existing_urls.add(url)  # Tambahkan ke set untuk memastikan tidak ada duplikasi

# Fungsi untuk membaca negara dari file
def read_countries_from_file(filename):
    try:
        with open(filename, 'r') as file:
            countries = [line.strip() for line in file.readlines()]
        return countries
    except FileNotFoundError:
        print(Fore.RED + f"File '{filename}' tidak ditemukan.")
        return []

# Fungsi untuk memproses bagian dari file dengan Selenium
def process_chunk(chunk, keyword, result_file):
    # Setup untuk WebDriver (Chrome) dengan opsi headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Set untuk menyimpan URL yang sudah ada
    existing_urls = set()

    for country in chunk:
        page_number = 0
        while True:
            urls = get_urls_from_page(page_number, keyword, country, driver, existing_urls)
            
            # Jika halaman berisi tepat 6 URL, anggap halaman kosong dan lanjut ke pencarian kata kunci berikutnya
            if len(urls) == 6:
                break
            
            # Jika tidak ada URL yang ditemukan, hentikan pencarian untuk kata kunci ini
            if not urls:
                break
            
            # Simpan URL yang ditemukan ke dalam file secara real-time, tanpa duplikat dan blacklist
            save_urls_to_file(urls, result_file)
            
            # Lanjutkan ke halaman berikutnya
            page_number += 1
            
            # Tambahkan waktu jeda antara permintaan untuk menghindari pemblokiran
            time.sleep(1)  # Meningkatkan waktu tidur untuk menghindari pemblokiran

    # Menutup driver setelah selesai
    driver.quit()

# Fungsi utama untuk memulai proses scraping dengan multithreading
def main():
    banner = Fore.GREEN + """
            $$$$$$$$\  $$$$$$\   $$$$$$\ $$\     $$\        $$$$$$\   $$$$$$\  $$$$$$$\  $$$$$$$$\ $$\   $$\ 
            $$  _____|$$  __$$\ $$  __$$\\$$\   $$  |      $$  __$$\ $$  __$$\ $$  __$$\ $$  _____|$$ |  $$ |
            $$ |      $$ /  $$ |$$ /  \__|\$$\ $$  /       $$ /  \__|$$ /  $$ |$$ |  $$ |$$ |      \$$\ $$  |
            $$$$$\    $$$$$$$$ |\$$$$$$\   \$$$$  /        $$ |      $$ |  $$ |$$ |  $$ |$$$$$\     \$$$$  / 
            $$  __|   $$  __$$ | \____$$\   \$$  /         $$ |      $$ |  $$ |$$ |  $$ |$$  __|    $$  $$<  
            $$ |      $$ |  $$ |$$\   $$ |   $$ |          $$ |  $$\ $$ |  $$ |$$ |  $$ |$$ |      $$  /\$$\ 
            $$$$$$$$\ $$ |  $$ |\$$$$$$  |   $$ |          \$$$$$$  | $$$$$$  |$$$$$$$  |$$$$$$$$\ $$ /  $$ |
            \________|\__|  \__| \______/    \__|           \______/  \______/ \_______/ \________|\__|  \__|  
    """
    
    print(banner)
    print(Fore.YELLOW + "Welcome to Laravel URL Scraper! https://t.me/darknetindogroup coded by @easycodex")
    
    # Minta input keyword dari pengguna
    keyword = input('Keyword file: ')  # Input the file with list of domains/keywords

    # Baca negara dari file country.txt
    country_file = "country.txt"
    countries = read_countries_from_file(country_file)
    
    if not countries:
        print(Fore.RED + "No Country Found, Closing.")
        return

    # Membagi daftar negara menjadi beberapa chunk
    num_threads = 5
    chunk_size = len(countries) // num_threads
    chunks = [countries[i:i + chunk_size] for i in range(0, len(countries), chunk_size)]

    result_file = "leakix-new.txt"
    
    # Menggunakan ThreadPoolExecutor untuk menjalankan pencarian untuk masing-masing negara secara paralel
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_chunk, chunk, keyword, result_file) for chunk in chunks]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(Fore.RED + f"Error in thread execution: {e}")
    
    print(Fore.GREEN + "Semua URL telah disimpan dalam file 'leakix.txt'.")

if __name__ == "__main__":
    main()
