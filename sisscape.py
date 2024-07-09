import requests
from bs4 import BeautifulSoup
import csv

def fetch_links():
    base_url = "https://sis.si-revizija.si/registry-enrollments/titles/3?page="
    links = []
    for page in range(1, 10):
        url = f"{base_url}{page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        td_elements = soup.find_all('td', class_='align-middle')
        
        for td in td_elements:
            form = td.find('form', attrs={'method': 'GET'})
            if form:
                action_url = form['action']
                if action_url not in links:
                    links.append(action_url)
    return links

def parse_link(link, csv_writer, fieldnames):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    card_body = soup.find('div', class_='card-body')
    if card_body:
        rows = card_body.find_all('div', class_='row')
        row_data = {field: '' for field in fieldnames} 
        row_data['Povezane osebe'] = []  
        row_data['Vrsta povezave'] = []  

        for row in rows:
            divs = row.find_all('div', recursive=False)
            h3 = None
            for div in divs:
                h4 = div.find('h4')
                span = div.find('span', class_='text-muted')
                if h4 and h4.text.strip() != 'Vrsta povezave' and span:
                    header = h4.text.strip()
                    if header in fieldnames:
                        row_data[header] = span.text.strip()
                if div.find('h3', class_='mb-0 border-bottom'):
                    h3 = div.find('h3', class_='mb-0 border-bottom').text.strip()
                if h4 and h4.text.strip() == 'Vrsta povezave' and h3: 
                    span_vp = div.find('span', class_='text-muted')
                    if span_vp:
                        row_data.setdefault('Povezane osebe', []).append(h3)
                        row_data.setdefault('Vrsta povezave', []).append(span_vp.text.strip())

        if 'Povezane osebe' in row_data:
            row_data['Povezane osebe'] = ', '.join(row_data['Povezane osebe'])
        if 'Vrsta povezave' in row_data:
            row_data['Vrsta povezave'] = ', '.join(row_data['Vrsta povezave'])
        row_data['SIS_URL'] = link  
        csv_writer.writerow(row_data)


def main():
    links = fetch_links()
    fieldnames = ["Ime", "Priimek", "Elektronski naslov", "Izobrazba", "Smer izobrazbe", 
                  "Fakulteta", "Registrska številka", "Ime podjetja", "Naslov", "Naziv",
                  "Datum izdaje dovoljenja", "Začetek veljavnosti dovoljenja", "Konec veljavnosti dovoljenja",
                  "Datum pravnomočnosti", "Datum preizkusnega roka", "Spletna stran",
                  "Povezane osebe", "Vrsta povezave", "SIS_URL"]  
    if links:
        with open('output.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for link in links:
                parse_link(link, writer, fieldnames)

if __name__ == "__main__":
    main()
