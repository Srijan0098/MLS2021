import matplotlib.pyplot as plt
import cv2
import pandas as pd

def displaycsv(path1,path2):
    ant=pd.read_csv(path1)
    for i in range(len(ant)):
        j=int(ant.iloc[i,0])
        img=cv2.imread(path2+"/"+"0"*(3-len(str(j)))+str(j)+".jpg")

        img = cv2.rectangle(img, (int(ant.iloc[i,1]),int(ant.iloc[i,2])), (int(ant.iloc[i,3]),int(ant.iloc[i,4])),(255,0,0),3)                      
        cv2.imwrite("annotated_frames/annotated_frames"+str(ant.iloc[i,0])+".jpg",img)
    
    