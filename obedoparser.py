#!/usr/bin/env python2
# -*- coding: utf8 -*-
"""
parsuj stranky restauracii a vyrob jednoduchu html stranku s ponukou obedov
"""

from datetime import datetime
from pyfiglet import Figlet
import bs4
import requests
import re
import locale
import time

locale.setlocale(locale.LC_ALL, 'sk_SK.utf8')


Dow = unicode(datetime.today().strftime('%A'), encoding='utf8')
dow = Dow.lower()
DOW = Dow.upper()


class Restaurant(object):
    def __init__(self, name, website, menupage=None):
        self.name = name
        self.website = website
        if not menupage:
            self.menupage = website
        else:
            self.menupage = menupage
        self.lunch_line = []

    def get_menupage(self, encoding=None):
        r = requests.get(self.menupage)
        if encoding:
            r.encoding = encoding
        # self.soup = bs4.BeautifulSoup(r. text, 'html5lib')
	# html5lib parser nepracuje spolahlivo v kombinacii s Hami restikou
        self.soup = bs4.BeautifulSoup(r. text, 'html')

    def return_menu_as_list(self):
        return self.lunch_line

    def extract_menu(self):
        pass


class LiveRestaurantParser(Restaurant):
    def extract_menu(self):
        self.get_menupage()
        whole_week = self.soup.select('.entry')[0]
        for day in whole_week.findAll('p'):
            if hasattr(day.strong, 'span'):
		if dow in day.strong.text.lower():
                    self.lunch_line = day.text.splitlines()[1:]
                    self.lunch_line = [x for x in self.lunch_line]
                    return


class HamiRestaurantParser(Restaurant):
    def extract_menu(self):
        output = []
        self.get_menupage()
        polievky = self.soup.findAll(text=re.compile('\.2016'))
	if not polievky:
	    print "No polievka found" 
	    return
        for pol in polievky:
	    if dow in pol.lower():
		polievka = pol
	        break
	else:
            return
        for line in polievka.next_elements:
            if hasattr(line, 'text'):
                if u'Vítame Vás' in line.text:
                    break
            if not line:
                continue
            if hasattr(line, 'format_string'):
                line = re.sub(r'<[^>]+>', '', unicode(line))
                line = unicode(line)

                line = line.strip()
                if '2016' in line:
                    break
                output.append(line)
            continue
            if not output:
                output.append(line)
            elif (str(line).strip() != output[-1].strip() and line and
                    re.search('^[0-9]+\. *[A-Za-z]+', line)):
                output.append(line.strip())
        self.lunch_line = [unicode(polievka)] + output


class BlackoutRestaurantParser(Restaurant):
    def extract_menu(self):
        self.get_menupage()
        if not dow in self.soup.text.lower():
            return
        menublock = self.soup.select('.et_pb_text')[0].h2.find_next().next_siblings
        menublock = [x for x in menublock if type(x) is
                     bs4.element.NavigableString and not re.search('<br/>$',
                                                                   x)]
        self.lunch_line = list(menublock)
        self.lunch_line = [unicode(x) for x in self.lunch_line]


class MagdalenPubRestaurantParser(Restaurant):
    def extract_menu(self):
        self.get_menupage(encoding='utf8')
        week_offer = self.soup.find('p', text='MAGDALEN PUB MENU ').parent
        output = []
        it = iter(re.split(r'<br/>', unicode(week_offer)))
        for line in it:
            if DOW in line:
                while True:
                    today = next(it)
                    if re.search(r' *[A-Z]+ *$', today):
                        break
                    output.append(unicode(today))
        self.lunch_line = output

restaurants = (LiveRestaurantParser('Live', 'http://www.restaurant-live.sk/'),
               HamiRestaurantParser('Hami', 'http://www.restauracia-hami.sk/'),
               BlackoutRestaurantParser('Blackout Bar',
                                        'http://blackoutbar.sk/'),
               MagdalenPubRestaurantParser('Magdalen Pub',
                                           'https://sk-sk.facebook.com/Magdal%C3%A9n-pub-122301724501731/')
               )

print('<html><head><meta charset="UTF-8"></head><body><pre>')

fig = Figlet()
fig.setFont(font='smscript')
print(fig.renderText(time.strftime('%H:%M')))

for restaurant in restaurants:
    fig = Figlet()
    fig.setFont(font='future')
    print(fig.renderText(restaurant.name))
    print('<a href="%s">web</a>' % restaurant.website)

    restaurant.extract_menu()
    output = restaurant.return_menu_as_list()
    if output:
        print('\n'.join([x.encode('utf8') for x in output[:]]))
    else:
        print('No data')
    print('*' * 30)
print('</pre></body></html>')
