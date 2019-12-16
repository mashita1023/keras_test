import math
import numpy as np
import pandas as pd

files = ["record-157587249.txt"]
output = 'output_1.csv'

size = 1000

loc_AP={}
loc_AP["0xc24"] =(200,200,2400)
loc_AP["0x40a1"]=(5461, 200, 2400)
loc_AP["0x5633"]=(5461,4634,2400)
loc_AP["0x5da9"]=(200, 4634,2400)



def read_Files(Files):
  data = []
  for file in Files:
    with open(file) as f:
      s = f.read()
      # 分割
      lines=s.split('\n')
      data.extend(lines)
  return data

def cal_STD(Data):
   std = 0
   ave = 0
   for i in range(size):
     if len(Data) - i > 0:
        ave = ave + int(Data[len(Data)-1-i])/size

   for i in range(size):
     if len(Data) - i > 0:
        std = std + (int(Data[len(Data)-1-i]) - ave )**2
   return std


def choose_3AP_STD(dic_dist, DATAS):
  tmp = 0
  id_rm = 0 
  keys = [];
  dic_dist_std = {}
  dic_dist_sdt_sorted = {}

  i = 0
  for id in dic_dist:
    dic_dist_std[id] = cal_STD(DATAS[i])
    i = i + 1

  dic_dist_std_sorted = sorted(dic_dist_std.items(), key=lambda x:x[1])

  for id in dic_dist_std_sorted:
    keys.append(id[0])

  return keys

def get_location_triangulation(dic_dist, keys):

   loc = (0,0,0,0)

   r1 = int(dic_dist[keys[0]])
   r2 = int(dic_dist[keys[1]])
   r3 = int(dic_dist[keys[2]])


   x1, y1, z1 = loc_AP[keys[0]]
   x2, y2, z2 = loc_AP[keys[1]]
   x3, y3, z3 = loc_AP[keys[2]]

   A1 = r1**2 - x1**2 - y1**2 - z1**2
   A2 = r2**2 - x2**2 - y2**2 - z2**2
   A3 = r3**2 - x3**2 - y3**2 - z3**2

   x21 = x2 - x1
   x31 = x3 - x1
   y21 = y2 - y1
   y31 = y3 - y1
   z21 = z2 - z1
   z31 = z3 - z1

   A21 = - (A2 - A1)/2
   A31 = - (A3 - A1)/2

   D = x21*y31 - y21*x31
   B0 = (A21*y31 - A31*y21)/D
   B1 = (y21*z21 - y31*z21)/D
   C0 = (A31*x21 - A21*x31)/D
   C1 = (x31*z21 - x21*z31)/D

   E = B1**2 + C1**2 +1
   F = B1*(B0 - x1) + C1*(C0-y1) -z1
   G = (B0 - x1)**2 + (C0-y1)**2 + z1**2 - r1**2

   if (F**2 - E*G) >= 0:

     z = (-F - math.sqrt(F**2 - E*G))/E
     #z = (-F + math.sqrt(F**2 - E*G))/E
     x = B0 + B1*z
     y = C0 + C1*z
     loc = (x, y, z,0)
   else:
     loc = (0, 0, 0, 0)
#     print("ERROR")
   return loc

# ---  main ---

# anchor id <- distance
dic_dist={}

# Array for each AP distance
AP0=[]
AP1=[]
AP2=[]
AP3=[]

datas = read_Files(files)
DATAS = (AP0, AP1,AP2,AP3)

a = np.array([0, 0, 0]).reshape(3,1)
print(a.shape)

i=0
for d in datas:
   line=d.split(',')
   if line[0] == "0":
      if len(dic_dist) > 3:

         keys = choose_3AP_STD(dic_dist, DATAS)

         Loc=get_location_triangulation(dic_dist, keys)
         if Loc != (0,0,0,0):
#           print(str(Loc[0])+","+str(Loc[1])+","+str(Loc[2]))
            b = np.array([Loc[0], Loc[1], Loc[2]]).reshape(3,1)
#            print(b)
            a = np.append(a, b, axis=1)
         else:
           print("ERROR:CAL")
      else:
         print("ERROR: Anchor(s) - " + str(len(dic_dist)))
      dic_dist.clear
      i=0

   if len(line) > 3:
      dic_dist[line[1]]=line[2]
      if i == 0:
         AP0.append(line[2])
      elif i == 1:
         AP1.append(line[2])
      elif i == 2:
         AP2.append(line[2])
      elif i == 3:
         AP3.append(line[2])

      i = i + 1


print(a.shape)
df = pd.DataFrame(a).T
print(df)
df.to_csv(output)