import requests
import cv2

regions = ['vn']
path = './image/20180511_0925031_slrp.jpg'


def detect_plate(path):
	with open(path, 'rb') as fp:
	    response = requests.post(
	    	'https://api.platerecognizer.com/v1/plate-reader/',
	        data=dict(regions=regions),  # Optional
	        files=dict(upload=fp),
	        headers={'Authorization': 'Token 11e12906b07074d87046cb0e3b530f55dd85a2c1'})
	    result = response.json()['results']
	    print(result)
# if len(result) > 0:
# 	for v in result:
# 		color = (randint(0, 255), randint(0, 255), randint(0, 255))
# 		xmin, xmax, ymin, ymax = v['box']['xmin'], v['box']['xmax'], v['box']['ymin'], v['box']['ymax']
# 		cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 3)
# 		cv2.putText(img, v['plate'].upper(), (xmin, ymin - 10), cv2.FONT_HERSHEY_DUPLEX, 0.8, color)
# 	while True:
# 		cv2.imshow("result", img)
# 		if cv2.waitKey(33) == 27:
# 			break
# else:
# 	print("Cannot regconize the plate!")