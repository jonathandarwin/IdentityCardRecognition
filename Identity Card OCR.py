import urllib
import re
from PIL import Image
import pytesseract
from resizeimage import resizeimage
import os
import cv2
import numpy as np
import mysql.connector

pytesseract.tesseract_cmd = '<YOUR_tesseract.exe_PATH>'

src_path = "<PATH>"

img_path = src_path + "YOUR_IMAGE_FILE_NAME.png"


def get_string(img_path):
    # Read image
    img = cv2.imread(img_path)

    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)

    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
            

    ret2,img = cv2.threshold(img,80,100,cv2.THRESH_BINARY)

    
    # Save Image
    cv2.imwrite(src_path + "thres.png", img)    
    

    # Getting text from image
    result = pytesseract.image_to_string(Image.open(src_path + "thres.png"))    
        
    return result


def get_name(result) :
    left = result.find('Nama',0)
    rawName = result[left+4:]
    rawName = rawName[:rawName.find('\n')]    
    name = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", rawName).lstrip().rstrip()
        
    return name

def get_NIK(result) :
    left = result.find('NIK',0)
    rawNIK = result[left+3:]
    rawNIK = rawNIK[:rawNIK.find('\n')]    
    NIK = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", rawNIK).lstrip().rstrip()
            
    return NIK



print ('--- Getting text from image ---')

result = get_string(img_path)
Name = get_name(result)
NIK = get_NIK(result)

flag = 1

if Name == '' :
    print 'Cannot get name'
    flag = 0
else :
    print 'Name : ' + Name

    
if NIK == '' :
    print 'Cannot get NIK'
    flag = 0
else :
    print 'NIK : ' + NIK


if flag == 1:
    verify = raw_input('Please verify your data. Type "Y" to confirm, Type "N" to cancel : ')

    if verify == 'Y' :
        print 'OK'
        db = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd="",
            database="OCR_Python"
        )

        cursor = db.cursor()

        query = "INSERT INTO User(Name, NIK) VALUES (%s,%s)"
        value = (Name, NIK)
        cursor.execute(query, value)
        db.commit()

        print 'Insert Success'

print ("------ Done -------")
