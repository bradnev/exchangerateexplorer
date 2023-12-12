#Scraper.  All data is from XE.com.
from urllib.request import urlopen
import numpy as np
import pymongo
import ssl #SSL does not work properly.  We will have an insecure connection but I do not care.
import time
#Ensure pymongo 3.11 is installed.


#Filter to be used to extract decimal values - Python's own don't like points.
numlist = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."]

#Function for filtering strings.
def numdec(i):
    if i in numlist:
        return True
    else:
        return False

scrapes = ["These are the highest points the exchange rate has been at in the last 30 and 90-day periods.",
"These are the lowest points the exchange rate has been at in the last 30 and 90-day periods.",
"These are the average exchange rates of these two currencies for the last 30 and 90 days.",
"These percentages show how much the exchange rate has fluctuated over the last 30 and 90-day periods."]
#We use this list to find the location of the desired values within our HTML document.

#Function for finding values inside the HTML tables present in each page.
def tablescrape(i,s):
    l3 = s.find(i)
    ss3 = s[l3:l3+600]
    l4 = ss3.find('</div></div></th><td>')
    ss4 = ss3[l4:l4+100]
    l5 = ss4.find('</td><td>')
    return ["".join(filter(numdec, ss4[l5-15:l5])), "".join(filter(numdec, ss4[l5:l5+15]))]

#Base variables and lists.
urlbase = "https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To="
currencies = ["CAD", "GBP", "EUR", "RUB", "INR", "JPY", "CNY", "AUD", "CHF", "KRW"]
names = ["Canadian Dollar", "Great Britain Pound", "Euro", "Russian Ruble", "Indian Rupee", "Japanese Yen", "Chinese Yuan", "Australian Dollar", "Swiss Franc", "South Korean Won"]
values = np.empty([len(currencies),9])

while 0==0:

    #Loop that extracts the data from each site and adds it to the Values table.
    for j in range(0, len(currencies)):

        url = urlbase + currencies[j]
        page = urlopen(url)
        html = page.read().decode("utf-8")
        l1 = html.find('1.00 US Dollar')
        ss1 = html[l1+50:l1+150] #Substring we can visually work with.  This will extract the conversion rate.  There appears to be a delay in the updating, however.
        l2 = ss1.find('<span class="faded-digits">')
        ss2 = ss1[l2-10:l2+35]
        values[j,0] = float("".join(filter(numdec, ss2)))
        for k in range(0,4):
            kval = tablescrape(scrapes[k],html)
            values[j,1+(2*k)] = float(kval[0])
            values[j,2+(2*k)] = float(kval[1])

    #Create the import dictionaries.
    data = []
    for j in range(0, len(currencies)): #define variables iteratively   
        data.append({ "_id": j+1, "Currency": names[j], "Exchange Rate (1 USD)": values[j,0], "30 Day High": values[j,1], "90 Day High": values[j,2], "30 Day Low": values[j,3],
                     "90 Day Low": values[j,4], "30 Day Average": values[j,5], "90 Day Average": values[j,6], "30 Day Volatility": values[j,7], "90 Day Volatility": values[j,8]})

    #Connect to the MongoDB database.
    uri = "mongodb+srv://robertneville083:h@cluster0.i6sbepa.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri, ssl_cert_reqs=ssl.CERT_NONE)
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!") #Good to keep this.
    
    except Exception as e:
        print(e)
    
    db = client.currency
    collection = db.currency #enter the collection
    oo = collection.delete_many({})
    ii = collection.insert_many(data)
    print("Successful Inserts: ", ii.inserted_ids)

    time.sleep(60*60*24) #1 day wait
