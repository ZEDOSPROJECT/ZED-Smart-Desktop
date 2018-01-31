#!/usr/bin/env python

import dbus
import time
import os
import subprocess

currentBSSID=""
lastWifiDigit=""
currentWifiDigit=""
notFirst=False
wallpaperCurrentCmd=""

homeDir=os.getenv("HOME")+"/.desktopProfiles/"

try:
	os.mkdir(homeDir)
	os.system("gsettings get org.mate.background picture-filename > ~/.desktopProfiles/config.wallpaper")	
except:
	pass

def getBSSID():
	bus = dbus.SystemBus()
	proxy = bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
	manager = dbus.Interface(proxy, "org.freedesktop.NetworkManager")

	all_aps = []
	devices = manager.GetDevices()
	for d in devices:
		dev_proxy = bus.get_object("org.freedesktop.NetworkManager", d)
		prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")

		state = prop_iface.Get("org.freedesktop.NetworkManager.Device", "State")
		if state <= 2:
		    continue

		iface = prop_iface.Get("org.freedesktop.NetworkManager.Device", "Interface")
		dtype = prop_iface.Get("org.freedesktop.NetworkManager.Device", "DeviceType")
		if dtype == 2:  
		    wifi_iface = dbus.Interface(dev_proxy, "org.freedesktop.NetworkManager.Device.Wireless")
		    wifi_prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")
		    
		    
		    connected_path = wifi_prop_iface.Get("org.freedesktop.NetworkManager.Device.Wireless", "ActiveAccessPoint")

		    aps = wifi_iface.GetAccessPoints()
		    for path in aps:
		        ap_proxy = bus.get_object("org.freedesktop.NetworkManager", path)
		        ap_prop_iface = dbus.Interface(ap_proxy, "org.freedesktop.DBus.Properties")
		        bssid = ap_prop_iface.Get("org.freedesktop.NetworkManager.AccessPoint", "HwAddress")

		        if not bssid in all_aps:
		            all_aps.append(bssid)

		        if path == connected_path:
		            currentBSSID="%s (%s)" % (bssid, iface)
		            return currentBSSID
		            
def getSSID():
	batcmd="iwgetid -r"
	return subprocess.check_output(batcmd, shell=True)[:-1]

while True:
	if not os.path.exists(os.getenv("HOME")+"/.config/zed/noSD"):
		os.system("clear")
		if wallpaperCurrentCmd!="":
			os.system(wallpaperCurrentCmd)
		try:
			currentWifiDigit=getBSSID()+getSSID()
			print "BSSID="+getBSSID()
			print "SSID="+getSSID()
		except:		
			currentWifiDigit=""
			print "Not connected!"
				
		if lastWifiDigit!=currentWifiDigit:
			if currentWifiDigit!="":
				recognized=False
				count=0
				for profiles in os.listdir(homeDir):
					count=count+1
					if profiles==currentWifiDigit[:17]:
						recognized=True	
				if recognized:
					fFile=homeDir+currentWifiDigit[:17]
					oIndicator=open(fFile,"r")
					cSSID=oIndicator.readline()
					oIndicator.close()
					os.rename(homeDir+cSSID,homeDir+getSSID())
					indicator = open(fFile,"w")
					indicator.write(getSSID())
					indicator.close()
					cSSID=getSSID()
					if os.path.exists(os.getenv("HOME")+"/.desktopProfiles/"+cSSID+"/firstWifi"):
						wallpaperCurrentCmd="gsettings get org.mate.background picture-filename > ~/.desktopProfiles/config.wallpaper"
						# Change config file of fisrt profile
						configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","r")
						configData=configFile.readlines()
						configFile.close()
						configData[7]='XDG_DESKTOP_DIR="$HOME/Desktop"\n'
				
						configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","w")
						configFile.writelines(configData)
						configFile.close()
						######################################
						os.system("killall caja")	
						getPath = open(os.getenv("HOME")+"/.desktopProfiles/config.wallpaper","r")			
						os.system('gsettings set org.mate.background picture-filename "'+getPath.readline()+'"')
						getPath.close()			
					else:
						# Change config file of not fisrt profile
						configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","r")
						configData=configFile.readlines()
						configFile.close()
						configData[7]='XDG_DESKTOP_DIR="$HOME/.desktopProfiles/'+cSSID+'/Desktop"\n'
				
						configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","w")
						configFile.writelines(configData)
						configFile.close()
						######################################
						os.system("killall caja")	
						getPath = open(os.getenv("HOME")+"/.desktopProfiles/"+cSSID+"/config.wallpaper","r")			
						os.system('gsettings set org.mate.background picture-filename "'+getPath.readline()+'"')
						getPath.close()			
						wallpaperCurrentCmd="gsettings get org.mate.background picture-filename > ~/.desktopProfiles/"+cSSID+"/config.wallpaper"
				else:
					os.system("zenity --question --text 'Create a desktop profile for "+getSSID()+"?'; echo $? > /tmp/result")
					ff = open("/tmp/result","r")
					result=int(ff.readline()[:-1])
					ff.close()
					if result==0:
						indicator = open(homeDir+"/"+currentWifiDigit[:17],"w")
						indicator.write(getSSID())
						indicator.close()
						os.mkdir(homeDir+getSSID())
						print(count)
						if count>1:
							#is not the first wifi profile
							os.mkdir(homeDir+getSSID()+"/Desktop")
							os.system("gsettings get org.mate.background picture-filename > ~/.desktopProfiles/"+getSSID()+"/config.wallpaper")
							fFile=homeDir+currentWifiDigit[:17]
							oIndicator=open(fFile,"r")
							cSSID=oIndicator.readline()
							oIndicator.close()
							os.rename(homeDir+cSSID,homeDir+getSSID())
							indicator = open(fFile,"w")
							indicator.write(getSSID())
							indicator.close()
							cSSID=getSSID()
							getPath = open(os.getenv("HOME")+"/.desktopProfiles/"+cSSID+"/config.wallpaper","r")			
							os.system('gsettings set org.mate.background picture-filename "'+getPath.readline()+'"')
							getPath.close()
							wallpaperCurrentCmd="gsettings get org.mate.background picture-filename > ~/.desktopProfiles/"+cSSID+"/config.wallpaper"
				
							# Change config file
							configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","r")
							configData=configFile.readlines()
							configFile.close()
							configData[7]='XDG_DESKTOP_DIR="$HOME/.desktopProfiles/'+cSSID+'/Desktop"\n'
				
							configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","w")
							configFile.writelines(configData)
							configFile.close()
							######################################
							os.system("killall caja")
						else:
							#is the first wifi profile
							os.system("gsettings get org.mate.background picture-filename > ~/.desktopProfiles/config.wallpaper")
							fFile=homeDir+currentWifiDigit[:17]
							oIndicator=open(fFile,"r")
							cSSID=oIndicator.readline()
							oIndicator.close()
							os.rename(homeDir+cSSID,homeDir+getSSID())
							os.system("echo 'fisrt wifi profile' > ~/.desktopProfiles/"+getSSID()+"/firstWifi")
							indicator = open(fFile,"w")
							indicator.write(getSSID())
							indicator.close()
							cSSID=getSSID()
							# Change config file
							configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","r")
							configData=configFile.readlines()
							configFile.close()
							configData[7]='XDG_DESKTOP_DIR="$HOME/Desktop"\n'
		
							configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","w")
							configFile.writelines(configData)
							configFile.close()
							######################################
							os.system("killall caja")
			
							getPath = open(os.getenv("HOME")+"/.desktopProfiles/config.wallpaper","r")			
							os.system('gsettings set org.mate.background picture-filename "'+getPath.readline()+'"')
							getPath.close()
							wallpaperCurrentCmd="gsettings get org.mate.background picture-filename > ~/.desktopProfiles/config.wallpaper"
			else:
				# Change config file
				configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","r")
				configData=configFile.readlines()
				configFile.close()
				configData[7]='XDG_DESKTOP_DIR="$HOME/Desktop"\n'
		
				configFile=open(os.getenv("HOME")+"/.config/user-dirs.dirs","w")
				configFile.writelines(configData)
				configFile.close()
				######################################
				os.system("killall caja")
			
				getPath = open(os.getenv("HOME")+"/.desktopProfiles/config.wallpaper","r")			
				os.system('gsettings set org.mate.background picture-filename "'+getPath.readline()+'"')
				getPath.close()
				wallpaperCurrentCmd="gsettings get org.mate.background picture-filename > ~/.desktopProfiles/config.wallpaper"
			
	lastWifiDigit=currentWifiDigit		
	time.sleep(1)
