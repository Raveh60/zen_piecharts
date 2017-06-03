import urllib.request
from bs4 import BeautifulSoup
import sched, time
import re

url = "http://zenpools.miningspeed.com/"

update_time = 120

out_file = "/var/www/html/index.html"

html_indent = "\t\t"

html_header = """
<html>
  <head>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart']});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart() {

        var data = google.visualization.arrayToDataTable([
"""
		
html_footer = """
        ]);

        var options = {
          title: 'TITLE'
        };

        var chart = new google.visualization.PieChart(document.getElementById('piechart'));

        chart.draw(data, options);
      }
    </script>
  </head>
  <body>
    <div id="piechart" style="width: 900px; height: 500px;"></div>
  </body>
</html>
"""

#====CODE===============================

class Pool:
	name = ""
	hashrate = 0.0

class NetInfos:
	poolList = []
	hashRate = 0.0

#---------------------------------------

def hashtxtToFloat(hashtxt):
	spaceIdx = hashtxt.index(' ')
	hash = float(hashtxt[:spaceIdx])
	if hashtxt[spaceIdx+1:][0] == 'K':
		hash /= 1000.0
	return hash

def parsePools(soup, outPoolList):
	tags = soup.findAll('td')
	tags_len = len(tags);
	idx = 0
	pool = None
	while (idx < tags_len):
		inc = 1
		if idx % 7 == 0:
			if pool != None:
				print("ERROR: parsePools ! (0)")
				return False
			pool = Pool()
			pool.name = tags[idx].text
		elif idx % 7 == 1:
			if pool == None:
				print("ERROR: parsePools ! (1)")
				return False
			
			hashtxt = tags[idx].text
			pool.hashrate = hashtxtToFloat(hashtxt)
			outPoolList.append(pool)
			pool = None
			inc = 6
		else:
			print("ERROR: parsePools ! (2)")
			return False
		idx += inc
	return True

#---------------------------------------

def getHashrate(soup):
	hashtags = soup.findAll(text=re.compile('NET hash'), limit=1)
	if len(hashtags) > 0:
		hashtxt = str(hashtags[0].encode('utf-8'))[16:]
		hashfloat = hashtxtToFloat(hashtxt)
		print(hashfloat)
		return hashfloat
	return 0.0

#---------------------------------------

def getPoolsAndHashrate(outNetInfos):
	with urllib.request.urlopen(url) as response:
		soup = BeautifulSoup(response.read(), "html.parser", from_encoding="utf-8")
		outNetInfos.hashrate = getHashrate(soup)
		return parsePools(soup, outNetInfos.poolList)
	print("ERROR: getPools !")
	return False

#---------------------------------------

def createHtml(poolList):
	outHtml = html_header;
	outHtml += html_indent + "['Pool',\t'Hashrate'],\n"
	for pool in poolList:
		outHtml += html_indent + "['" + pool.name + "',\t" + str(pool.hashrate) + "],\n"
	outHtml += html_footer;
	return outHtml

#---------------------------------------
	
def writeHtml(htmlText):
	with open(out_file, "w") as text_file:
		print(htmlText, file=text_file)

#---------------------------------------

# MAIN

s = sched.scheduler(time.time, time.sleep)
def updatePools(sc): 
	netInfos = NetInfos()
	if getPoolsAndHashrate(netInfos) and len(netInfos.poolList) > 0:
		print("Found", len(netInfos.poolList), "pools!")
		htmlText = createHtml(netInfos.poolList)
		htmlText = htmlText.replace("TITLE", "Zencash network hasrate : " + str(netInfos.hashrate) + " MSol/s")
		writeHtml(htmlText)
	s.enter(update_time, 1, updatePools, (sc,))

s.enter(1, 1, updatePools, (s,))
s.run()
