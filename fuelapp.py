# rss parameters and usagefor FuelWacth defined by: https://www.fuelwatch.wa.gov.au/tools/rss 

import feedparser
import json
import webbrowser
from datetime import date
from urllib.parse import urlencode

def fuelappException(Exception):
    pass

VALID_PRODUCTS = {
    "Unleaded Petrol" : 1,
    "Premium Unleaded" : 2,
    "Diesel" : 4,
    "LPG" : 5,
    "98 RON" : 6,
    "E85" : 10,
    "Brand Diesel" : 11,
}

# Captures data from FuelWatch's API for a given location and returns each entry with only the desired data
def get_fuel(location, tomorrow=False, product_id=VALID_PRODUCTS["Unleaded Petrol"]):
    if product_id not in VALID_PRODUCTS.values():
        raise fuelappException("bad product code")
    
    q = urlencode( 
        {
            "Product"   : product_id,
            "Suburb"    : location,
            "Day"       : "tomorrow" if tomorrow else "today",
        }
    )
    
    url = f"http://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?{q}"
    data = feedparser.parse(url)

    return [
        {
            "price"     : stuff["price"],
            "location"  : stuff["location"],
            "address"   : stuff["address"],
            "day"       : "tomorrow" if tomorrow else "today",
        } for stuff in data["entries"]
    ]

# this function pulls today and tomorrow prices from FuelWatch's API and generates an HTML table
# using each entry. Data captured by the table is defined by the function get_fuel()
def generate_fuel_table_html(location):
    feed1 = get_fuel(location, tomorrow=False)
    feed2 = get_fuel(location, tomorrow=True)
    feed_sorted = sorted(feed1 + feed2, key=lambda x: x["price"])

    # use the keys returned in each entry to auto generate the table
    keys = [key for key in feed_sorted[0].keys()]

    # for each entry, using the order of keys as automatically pulled,
    # create the table rows 
    html_fuel_table = "<tr>" + "".join(f'''<th>{key}</th>''' for key in keys) + "</tr>\n"
    html_fuel_table += "<tr>".join(
    "".join(f'''<td>{entry[key]}</td>''' for key in keys) + "</tr>\n"
    for entry in feed_sorted)

    return html_fuel_table

def main():
    location = "Thornlie"

    #html body
    my_html = f'''
    <html>
    <head>
        <style>

        h1 {{text-align: center;}}

        table {{
            font-family: arial, sans-serif;
            border-collapse: collapse;
            width: 100%;
        }}

        td, th {{
            border: 1px solid #dddddd;
            text-align: center;
            padding: 8px;
        }}

        tr:nth-child(even) {{
            background-color: #dddddd;
        }}

        </style>
    </head>

    <body>
    <h1>Gas Prices at {location} ({date.today()})</h1>
        <table>
            {generate_fuel_table_html(location)}
        </table>
    </body>
    </html>
    '''

    #render and open the html
    with open(f"render-{date.today()}.html", "w") as f:
        f.write(my_html)
    
    webbrowser.open(f"render-{date.today()}.html")

if __name__ == "__main__":
    main()