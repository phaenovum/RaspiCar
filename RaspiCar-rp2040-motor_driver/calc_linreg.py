import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


voltage = [1287, 1287, 1277, 1267, 1267, 1257, 1247, 1237, 1227, 1217, 1207,
           1197, 1187, 1177, 1166, 1157, 1146, 1137, 1127, 1116, 1107, 1097,
           1087, 1077, 1067, 1057, 1046, 1036, 1026, 1017, 1006,  996,  986,
            976,  966,  956,  946,  936,  926,  916,  906,  896, 1166, 1216,
           1257, 1297, 1347, 1357, 1367, 1377 ]
adc = 	  [12414, 12423, 12148, 11888, 11887, 11614, 11343, 11050, 10819, 10545,
           10281, 10003,  9740,  9461,  9200,  8922,  8645,  8370,  8096,  7822,
            7560,  7285,  7013,  6747,  6497,  6239,  5960,  5700,  5425,  5162,
            4885,  4601,  4334,  4062,  3781,  3519,  3244,  2970,  2707,  2433,
            2170,  1926,  9199, 10545, 11595, 12677, 14025, 14297, 14563, 14840]

df = pd.DataFrame(voltage)
df.columns = ['voltage']
df['adc'] = adc

linreg = LinearRegression()
linreg.fit(pd.DataFrame(df['adc']), df['voltage'])
print("Slope:", linreg.coef_)
slope_int = round(linreg.coef_[0] * 10000)
print("Slope int:", slope_int)
intercept = round(linreg.intercept_)
print("Intercept:", intercept)
x_range = pd.DataFrame([df['adc'].min(), df['adc'].max()])
x_range.columns = ['adc']
y_range = linreg.predict(x_range)

"""
fig, ax = plt.subplots()
ax.scatter(df['adc'], df['voltage'], marker='+')
ax.plot(x_range, y_range, color='red')
ax.set_ylabel("Voltage")
ax.set_xlabel("ADC")
plt.show()
"""
for idx, x in enumerate([int(x_range.iloc[0]['adc']), int(x_range.iloc[1]['adc'])]):
    print(x, y_range[idx], int(intercept + slope_int * x / 10000))
#df['voltage'] = voltage
#df['adc'] = adc
