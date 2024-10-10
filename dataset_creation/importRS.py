from lxml import html
import requests
import datetime
from RStoLWPandPWV import RStoLWPandPWV
from RStoTB import RStoTB
import re
import math
import matplotlib.pyplot as plt


class Sounding:
    def __init__(self,station):
        self.day_time = float('nan')
        self.station = station
        self.P = []
        self.z = []
        self.T = []
        self.RH = []
        self.PWV = []
        self.LWP = []
        self.Q = []
        self.TB = []
        
    def addTB(self):
        self.TB = RStoTB(self.P,self.z,self.T,self.RH,self.Q)[0]

        
class Dataset:
    def __init__(self,station,day_time,Psurf,Tsurf,RHsurf,TB,LWP,PWV = None):
        self.station = station
        self.day_time = day_time
        self.Psurf = Psurf
        self.Tsurf = Tsurf
        self.RHsurf = RHsurf # added
        self.TB = TB
        self.LWP = LWP
        self.PWV = PWV
        
class Station:
    def __init__(self,number):
        self.number = number
        self.name = ''
        self.latitude = float('nan')
        self.longitude = float('nan')
        self.elevation = float('nan')


        
def importRS(year,month,stnnum):    
    year = str(year)
    month = '%02d'%month
    stnnum = '%05d'%stnnum
    start='all'
    end='0200' #not important, just need to be set to something to get the url
    region = 'np' #not important, same

    # extract data from university of Wyoming websit
    soundings = []
    path = 'http://weather.uwyo.edu/cgi-bin/sounding?region='+region+'&TYPE=TEXT%3ALIST&YEAR='+year+'&MONTH='+month+'&FROM='+start+'&TO='+end+'&STNM='+stnnum
    page = requests.get(path)
    tree = html.fromstring(page.content)
    headers = tree.xpath('//h2/text()')
    data = tree.xpath('//pre/text()')

    nsoundings = len(headers)


    if nsoundings == 0:
        print('Warning: no soundings found at this path: '+path)
        
        return []
    
    else:
        station = Station(stnnum)
        station.name = re.search('(.+?)Observations',headers[0]).group(1)[7:]

        station_info = data[1].split('\n')      

        for item in station_info:
            if 'latitude' in item:
                station.latitude = float(item.split()[-1])
            elif 'longitude' in item:
                station.longitude = float(item.split()[-1])
            elif 'elevation' in item:
                station.elevation = float(item.split()[-1])

        if station.latitude != station.latitude:
            print('Warning: no latitude for this station' + stnnum)
        if station.longitude != station.longitude:
            print('Warning: no longitude for this station' + stnnum)
        if station.elevation != station.elevation:
            print('Warning: no elevation for this station' + stnnum)



        for i in range(nsoundings):
            rs = Sounding(station)
            endheader = headers[i][-15:]
            time = int(endheader[0:2])
            day = int(endheader[4:6])
            rs.day_time = datetime.datetime(int(year),int(month),day,time)

            datai = data[2*i].split('\n')[5:]
            P = []
            z = []
            T = []
            RH = []
            Qv = []
            
            for line in datai:
                linelist = line.split()
                if len(linelist) == 11:
                    P.append(100*float(linelist[0]))
                    z.append(float(linelist[1]))
                    T.append(min(float(linelist[2]),299))
                    RH.append(min(float(linelist[4]),199))
                    Qv.append(float(linelist[5]))

            if len(P)>10:        
                (rs.P,rs.z,rs.T,rs.RH,rs.PWV,rs.LWP,rs.Q) = RStoLWPandPWV(P,z,T,RH,Qv)
                rs.addTB()

                soundings.append(Dataset(rs.station,rs.day_time,rs.P[0],rs.T[0],rs.RH[0],rs.TB,rs.LWP,rs.PWV))

        return soundings

    

# Here is a subset of station numbers
# Full list is in radiosonde-station-list.txt (need to extract the 5-digit WMO ID)
stations_list = [ 2365,  3354,  4220,  4417,  6011, 10618, 10771, 10868, 11035,
       11520, 11747, 11952, 12843, 13275, 15420, 16080, 16113, 16245,
       16429, 17030, 17130, 17240, 20046, 20674, 22820, 24266, 24507,
       24688, 24908, 25123, 26038, 26702, 27199, 27730, 29231, 30372,
       31510, 31873, 32150, 32389, 32618, 33041, 35671, 36096, 36872,
       37011, 38341, 40375, 40430, 40437, 40745, 40754, 40766, 40800,
       40848, 41024, 41316, 42027, 42101, 42182, 42299, 42379, 42492,
       42667, 43003, 43041, 43295, 44231, 44292, 48855, 50953, 51076,
       51709, 51839, 52818, 55299, 56964, 58027, 59211, 60018, 60155,
       60390, 60571, 60680, 61687, 61995, 65578, 67083, 68263, 68424,
       68816, 68842, 70273, 71722, 71811, 71816, 71906, 71908, 71924,
       72230, 72327, 72365, 72469, 72489, 72520, 72558, 72572, 72634,
       72672, 73033, 74389, 74560, 76225, 78954, 82599, 82917, 83525,
       83554, 83768, 83779, 83827, 83928, 85586, 89009, 89532, 89571,
       89592, 89611, 89664, 93112, 93417, 93844, 94203, 94461, 94638,
       94975, 95527, 96035, 96253, 96509, 97502, 97560, 98328, 98433]


if __name__=='__main__':
	for yr in range(2000,2019): 
		for stnum in stations_list:
		print('year = %i, stn = %i' %(yr,stnum))
		soundings = []
		for month in range(1,13):
			try:
			    soundings.append(importRS(yr,month,stnum))
			except:
			    'Warning: error was raised for stn = %i, yr = %i, month = %i'

		soundings = [s for s_month in soundings for s in s_month]

		if len(soundings) !=0:

			with open('/data/anneclaire/LWP_dataset/%i%i.txt'%(yr,stnum),'w') as myf:
			    myf.write(soundings[0].station.name + '\t' + str(soundings[0].station.number) + '\t' + str(soundings[0].station.latitude) + '\t' + str(soundings[0].station.longitude) + '\t' + str(soundings[0].station.elevation) + '\n')
			    myf.write('day of year \t Tsurf \t Psurf \t RHsurf \t LWP \t PWV \t TB\n')
			    for i in range(len(soundings)):
			        myf.write(soundings[i].day_time.strftime('%Y-%m-%d-%H') + '\t' + str(soundings[i].Tsurf) + '\t' + str(soundings[i].Psurf) + '\t' + str(soundings[i].RHsurf) + '\t' + str(soundings[i].LWP) + '\t' + str(soundings[i].PWV) + '\t' + str(soundings[i].TB[0]) + '\n')


