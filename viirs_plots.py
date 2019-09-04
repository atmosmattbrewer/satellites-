from satpy import Scene
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from metpy.plots import USCOUNTIES
from satpy import find_files_and_readers
from datetime import datetime
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
from satpy.writers import cf_writer
from satpy.writers import get_enhanced_image
from metpy.plots import USCOUNTIES # Make sure metpy is updated to latest version.
import xarray as xr
from pathlib import Path
import pyart


el = Path("/export/home/mbrewer/Documents/GMTED2010_15n030_0125deg.nc")
rad = Path("/export/home/mbrewer/Documents/radar_files/KBBX20181108_213133_V06")

radar = pyart.io.read_nexrad_archive(rad)
#gf = pyart.filters.GateFilter(radar)
#gf.exclude_transition()
#gf.exclude_above('reflectivity', 100) #Mask out dBZ above 100
#gf.exclude_below('reflectivity', 5) #Mask out dBZ below 5
#despec = pyart.correct.despeckle_field(radar, 'reflectivity',gatefilter = gf, size = 20) #The despeckling mask routine that takes out small noisey reflectivity bits not near the main plume

elev = xr.open_dataset(el)
scn = Scene(
        filenames=glob("npp/*"),
        reader='viirs_l1b')
scn.load(['true_color', 'I02'])
new_scn = scn.resample('northamerica')
var = get_enhanced_image(new_scn['true_color']).data
var = var.transpose('y', 'x', 'bands')


st = str(scn.attrs['sensor'])[2:-2]

fig = plt.figure(figsize=(20, 10), dpi=200)
crs = new_scn['true_color'].attrs['area'].to_cartopy_crs()
ax = fig.add_subplot(1, 1, 1, projection=crs)

ax.imshow(var.data, extent=(var.x[0], var.x[-1], var.y[-1], var.y[0]), origin='upper')
#ax.add_feature(cfeature.COASTLINE.with_scale('10m'), edgecolor='orange')
#ax.add_feature(cfeature.STATES.with_scale('10m'), edgecolor='orange')
#ax.add_feature(USCOUNTIES.with_scale('500k'), edgecolor='orange', alpha = .75)
ax.set_extent([-122.5, -120.5, 39., 40.5], crs=ccrs.PlateCarree())
display = pyart.graph.RadarMapDisplayCartopy(radar)
display.plot_ppi_map('reflectivity', 0,  resolution = 'h', #The "0" is the lowest PPI scan, increasing this number increases the scanning elevation
             vmin=-10, vmax=64, colorbar_flag = False, fig = fig, ax=ax,alpha = .08, projection = crs)#, gatefilter = gf)
display.plot_colorbar(label_size = 15 ,ticklabel_size = 12,  ax =ax)

plt.title('Satellite: %s'%(st), loc='left', fontweight='bold', fontsize = 18)
plt.title('Radar: KBBX', loc='center', fontsize = 15)
plt.title('Satellite Time:\n%s\nRadar Time:\n%s' % (scn.attrs['start_time'].strftime("%Y-%m-%d %H:%M:%S"),radar.time['units'][14:24] + ' ' + radar.time['units'][25:]), loc='right', fontsize = 12)
#ax.text(0.25, 1.0, )

plt.show()
