import numpy as np
import cv2

path_img = 'picture.jpg'
img = cv2.imread(path_img)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# define range of blue color in HSV
lower_blue = np.array([0,120,50])
upper_blue = np.array([10,255,255])

# Threshold the HSV image to get only blue colors
mask = cv2.inRange(hsv, lower_blue, upper_blue)

contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
count = 0;
for c in contours:
   rect = cv2.boundingRect(c)
   x,y,w,h = rect
   area = w * h

   epsilon = 0.08 * cv2.arcLength(c, True)
   approx = cv2.approxPolyDP(c, epsilon, True)

   if area > 3000:
      #cv2.drawContours(img, [approx], -1, (0, 0, 255), 5)
      cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 5)
      print('approx', approx)
      count = count +1
      #for x in range(0, len(approx)):
         #cv2.circle(img, (approx[x][0][0], approx[x][0][1]), 30, (0,0,255), -1)

# cv2.drawContours(img, contours, -1, (0,255,0), 5)
cv2.imwrite('output.png',mask)
cv2.imwrite('outputp1.png',img)
print (count)
#cv2.imshow('output.png',mask)
# cv2.imshow('hsv',img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
