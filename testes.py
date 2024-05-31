from findpeaks import findpeaks
X = [9,60,377,985,1153,672,501,1068,1110,574,135,23,3,47,252,812,1182,741,263,33]
fp = findpeaks(method='peakdetect',lookahead=1,interpolate=10)
results = fp.fit(X)
fp.plot()

# 2D array example
#from findpeaks import findpeaks
#X = fp.import_example('2dpeaks')
#results = fp.fit(X)
#fp.plot()

# Image example
from findpeaks import findpeaks
fp = findpeaks(method='topology',imsize=(300,300),denoise='fastnl',params={'window': 30})
X = fp.import_example('2dpeaks_image')
results = fp.fit(X)
fp.plot()

# Plot each seperately
fp.plot_preprocessing()
fp.plot_persistence()
fp.plot_mesh()


