import os
import datetime
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def get_items_from_index():
    with open('index.html', 'r') as f:
        soup = BeautifulSoup(f.read(), 'lxml')

    writings = []
    writings_header = soup.find('h2', id='writings')
    if writings_header:
        dl = writings_header.find_next_sibling('dl')
        if dl:
            for dt in dl.find_all('dt'):
                a = dt.find('a')
                if a:
                    title = a.text
                    link = a['href']
                    dd = dt.find_next_sibling('dd')
                    description = dd.text if dd else ''
                    writings.append({'title': title, 'link': link, 'description': description, 'is_blog': True})

    links = []
    links_header = soup.find('h2', id='links')
    if links_header:
        dl = links_header.find_next_sibling('dl')
        if dl:
            for dt in dl.find_all('dt'):
                a = dt.find('a')
                if a:
                    title = a.text
                    link = a['href']
                    dd = dt.find_next_sibling('dd')
                    description = dd.text if dd else ''
                    links.append({'title': title, 'link': link, 'description': description, 'is_blog': False})
    
    return writings + links

def get_pub_date(blog_path):
    try:
        with open(blog_path, 'r') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
        
        date_str = soup.find('h3').text
        # Assuming date format is DD-MM-YYYY
        return datetime.datetime.strptime(date_str, '%d-%m-%Y')
    except Exception as e:
        print(f"Could not parse date from {blog_path}: {e}")
        return datetime.datetime.now()


def generate_feed():
    items = get_items_from_index()
    
    rss = Element('rss', version='2.0', attrib={'xmlns:atom': 'http://www.w3.org/2005/Atom'})
    channel = SubElement(rss, 'channel')
    
    SubElement(channel, 'title').text = 'Anurag Yadav'
    SubElement(channel, 'link').text = 'https://anurag-y.github.io'
    SubElement(channel, 'description').text = 'Writings and links from Anurag Yadav'
    SubElement(channel, 'language').text = 'en-us'
    
    atom_link = SubElement(channel, 'atom:link', href='https://anurag-y.github.io/feed.xml', rel='self', type='application/rss+xml')

    for item in items:
        item_elem = SubElement(channel, 'item')
        SubElement(item_elem, 'title').text = item['title']
        
        # Prepend base URL if link is relative
        base_url = 'https://anurag-y.github.io'
        if item['link'].startswith('/'):
            full_link = base_url + item['link']
        else:
            full_link = item['link']
        
        SubElement(item_elem, 'link').text = full_link
        SubElement(item_elem, 'guid').text = full_link
        SubElement(item_elem, 'description').text = item['description']

        if item['is_blog']:
            # Assuming blog links are relative paths from root
            blog_path = item['link'].lstrip('/')
            pub_date = get_pub_date(blog_path)
        else:
            # For external links, use current time
            pub_date = datetime.datetime.now()

        SubElement(item_elem, 'pubDate').text = pub_date.strftime('%a, %d %b %Y %H:%M:%S GMT')

    # Prettify XML
    xml_str = tostring(rss, 'utf-8')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open('feed.xml', 'w') as f:
        f.write(pretty_xml_str)

if __name__ == '__main__':
    generate_feed()
    print("feed.xml has been updated.")

