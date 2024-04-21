import pandas as pd
from datetime import datetime
df = pd.read_csv('output2.csv')
df_ex = pd.read_excel('пп_станции.xlsx')

# for i in range(321):
#     print(i,df_ex['Станция'][df_ex.index[df_ex[datetime.fromtimestamp(int(df['Time'][df.index[df['Info']==i]][:1])).replace(hour=0)]==int(df['Count'][df.index[df['Info']==i]][:1])]])

# embed = {}
# k = 0
# for el in sorted(df_ex['Станция']):
#     embed[el]=k
#     k+=1
# print(embed)

a = [1, 2, 3, 4, 5, 6, 7, 8]
b = a[::2]
print(b)