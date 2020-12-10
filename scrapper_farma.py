from datetime import datetime
import pandas as pd
import os
import time
from progress.bar import ChargingBar
from selenium import webdriver
from random import randint

def catalogue_leaves(entry, driver):
    driver.get(entry)
    time.sleep(10)  
    productos = driver.find_elements_by_xpath('//a[@class="product-item-link"]')
    list_catalogue = [i.get_attribute('href') for i in productos ]   

    return(list_catalogue) 

def scrapper_pigmento(url, driver):
    try:
        driver.get(url)
        time.sleep(3)
        pigmento_product = {}

        # NOMBRE DEL PRODUCTO
        name = driver.find_element_by_xpath('//h1[@class="page-title"]').text
        if name is None:
            pigmento_product['name'] = None
        else:
            pigmento_product['name'] = name

        # MARCA DEL PRODUCTO
        try:
            brand = driver.find_element_by_xpath('//ul[@class="product-brands"]').text
            pigmento_product['brand'] = brand

        except Exception as e:
            pigmento_product['brand'] = None 

        # PRECIO DE PRODUCTO
        n_price = discount_img = driver.find_elements_by_xpath('//div[@class="price-box price-final_price"]/span')
        if len(n_price) == 1:
            price = driver.find_element_by_xpath('//div[@class="price-box price-final_price"]/span').text
            if price is None:
                pigmento_product['price'] = None
                pigmento_product['discount_price'] = None
            else:
                pigmento_product['price'] = price
                pigmento_product['discount_price'] = None

        # PRECIO DESCUENTO DEL PRODUCTO
        else:
            price = driver.find_element_by_xpath('//span[@class="old-price"]').text
            discount_price = driver.find_element_by_xpath('//span[@class="special-price"]').text   
            if price is None:
                pigmento_product['price'] = None
                pigmento_product['discount_price'] = None
            else:
                pigmento_product['price'] = price
                pigmento_product['discount_price'] = discount_price   

        # IMAGEN DEL DESCUENTO DEL PRODUCTO
        try:
            discount_img = driver.find_element_by_xpath('//img[@class="amasty-label-image"]').get_attribute('src')
            pigmento_product['discount_img'] = discount_img   
        except Exception as e:
            pigmento_product['discount_img'] = None
    
        # IMAGEN DEL PRODUCTO
        try:
            img = driver.find_element_by_xpath('//img[@class="fotorama__img"]').get_attribute('src')
            pigmento_product['img'] = img

        except Exception as e:
            pigmento_product['img'] = None
       
        
        # DESCRIPCION DEL PRODUCTO
        try:
            descrip = driver.find_element_by_xpath('//div[@class="product attribute description"]').text
            pigmento_product['descrip'] = descrip

        except Exception as e:
            pigmento_product['descrip'] = None
            pigmento_product['log'] = e   
        

        pigmento_product['url'] = url

        pigmento_product['download'] = datetime.now()    

        return pigmento_product        
            
    except Exception as e:
        print(f' Error {e}')
        product_error = {}
        product_error['url'] = url
        product_error['log'] = e    
        return product_error
        
def load_data(name, data_clean):
    date = datetime.now().strftime('%Y_%m_%d')
    file_name = '{name}_{datetime}.csv'.format(name=name, datetime=date)  

    if os.path.isfile (f'{file_name}'):
        print(f'loading data in {file_name}....\n' )       
        data_clean.to_csv(file_name, mode='a', header=False)
        print('COMPLETED')
    else:
        print(f'\nCreate {file_name}....\n')
        data_clean.to_csv(file_name, encoding='utf-8')
        print('COMPLETED')

def scrapper_farma(option, url_products, driver):
    print(f'\n\n Starting download of Pigmento')

    if option == 0:
        option_txt = 'pigmento'
    else:
        option_txt = 'pigmento_filter'

    product_pigmento = []
    error = []
    
    print(f'{len(url_products)} products')
    print(f'\n Start of the process: {datetime.now()}\n')
    start = datetime.now()
    bar = ChargingBar('Scrapeando:', max=len(url_products))
    for i in url_products:      
        time.sleep(randint(5,10))
        data = scrapper_pigmento(i, driver)
        if len(data) == 2:
            error.append(data)
        else:
            product_pigmento.append(data)

        bar.next()
    
    bar.finish() 

    df = pd.DataFrame(product_pigmento)
    load_data(option_txt, df)

    if len(error) > 0:
        df = pd.DataFrame(error)
        load_data('Errores_pigmento', df)

    print(f'{len(error)} error found')
    print(f'{datetime.now()}')
    end = datetime.now()
    print(f'\nEnd of the process: {end - start}\n')   

def validate():
    var_enter = int(input('\n What you want to do? \n\n 0 .-Scrapper all pigmento \n 1 .-Scrapper only category of pigmento \n 2 .-Exit \n\n Only option number --->> '))
    while var_enter > 1:
        if var_enter == 2:
            print('\n Bye bye')
            break
        print('\n Error, enter the number of a valid option')
        var_enter = int(input('\n  --->> '))

    return var_enter    

def run():

    option = validate()

    if option == 0:
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')
        driver = webdriver.Chrome(executable_path='/Users/Sistemas/Desktop/chromedriver_win32/chromedriver', options=options)
        #All products
        link = catalogue_leaves('https://perfumeriaspigmento.com.ar/super-promociones?p=3&product_list_limit=all',driver)

        scrapper_farma(option, link, driver)
        driver.close()

    else:
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')
        driver = webdriver.Chrome(executable_path='/Users/Sistemas/Desktop/chromedriver_win32/chromedriver', options=options)
        #Only filter
        link = catalogue_leaves(input('\n enter link to download--->> '), driver)

        scrapper_farma(option, link, driver)
        driver.close()
             
if __name__ == "__main__":
    run()