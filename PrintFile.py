from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

collimatorFile = open("//10.35.209.1/Varios/Scripts/ESAPI/colimador.txt","r")
collimatorLines = collimatorFile.readlines()
collimatorX = []
collimatorY = []
collimatorZ = []
for line in collimatorLines:
    collimatorX.append(float(line.split(' ')[0]))
    collimatorY.append(float(line.split(' ')[2]))
    collimatorZ.append(-float(line.split(' ')[1]))

couchFile = open("//10.35.209.1/Varios/Scripts/ESAPI/mesa.txt","r")
couchLines = couchFile.readlines()
couchX = []
couchY = []
couchZ = []
for line in couchLines:
    couchX.append(float(line.split(' ')[0]))
    couchY.append(float(line.split(' ')[2]))
    couchZ.append(-float(line.split(' ')[1]))

bodyFile = open("//10.35.209.1/Varios/Scripts/ESAPI/body.txt","r")
bodyLines = bodyFile.readlines()
bodyX = []
bodyY = []
bodyZ = []
for line in bodyLines:
    bodyX.append(float(line.split(' ')[0]))
    bodyY.append(float(line.split(' ')[2]))
    bodyZ.append(-float(line.split(' ')[1]))

ax.scatter(collimatorX, collimatorY, collimatorZ, color = '#e5db99', marker='.', linewidths = 0)
ax.scatter(couchX, couchY, couchZ, color='#e299e5', marker='.', linewidths = 0)
ax.scatter(bodyX, bodyY, bodyZ, color='#6bd3b1', marker='.', linewidths = 0)
ax.set_xlabel('X')
ax.set_ylabel('Z')
ax.set_zlabel('Y')
plt.show()
