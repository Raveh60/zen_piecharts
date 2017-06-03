import urllib.request
from bs4 import BeautifulSoup
import sched, time

url = "http://zenpools.miningspeed.com/"

update_time = 20

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
          title: 'Zencash network hashrate : 3.07 MSol/s'
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

def parsePools(tags, outPoolList):
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
			spaceIdx = hashtxt.index(' ')
			hash = float(hashtxt[:spaceIdx])
			if hashtxt[spaceIdx+1:][0] == 'K':
				hash /= 1000.0
			pool.hashrate = hash
			outPoolList.append(pool)
			pool = None
			inc = 6
		else:
			print("ERROR: parsePools ! (2)")
			return False
		idx += inc
	return True

def getPools(outPoolList):
	with urllib.request.urlopen(url) as response:
		soup = BeautifulSoup(response.read(), "html.parser", from_encoding="utf-8")
		tags = soup.findAll('td')
		return parsePools(tags, outPoolList)
	print("ERROR: getPools !")
	return False

def createHtml(poolList):
	outHtml = html_header;
	outHtml += html_indent + "['Pool',\t'Hashrate'],\n"
	for pool in poolList:
		outHtml += html_indent + "['" + pool.name + "',\t" + str(pool.hashrate) + "],\n"
	outHtml += html_footer;
	return outHtml
	
def writeHtml(htmlText):
	with open(out_file, "w") as text_file:
		print(htmlText, file=text_file)
	
	

# MAIN

s = sched.scheduler(time.time, time.sleep)
def updatePools(sc): 
	poolList = []
	if getPools(poolList) and len(poolList) > 0:
		print("Found", len(poolList), "pools!")
		htmlText = createHtml(poolList)
		writeHtml(htmlText)
	s.enter(update_time, 1, updatePools, (sc,))

s.enter(update_time, 1, updatePools, (s,))
s.run()
