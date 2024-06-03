import cv2


test=cv2.imread('fetched.png',cv2.IMREAD_COLOR)
testTarget = cv2.imread('TestTarget.png',cv2.IMREAD_COLOR)
target = cv2.imread('Target.png',cv2.IMREAD_COLOR)

sift = cv2.SIFT_create()
kp_1, desc_1 = sift.detectAndCompute(test, None)
kp_2, desc_2 = sift.detectAndCompute(target, None)

index_params = {"algorithm":0, "trees":5}
search_params = dict()
flann = cv2.FlannBasedMatcher(index_params, search_params)

matches = flann.knnMatch(desc_1, desc_2, k=2)

good_points = []
ratio = 0.9
for m, n in matches:
    if m.distance < ratio*n.distance:
        good_points.append(m)

result = cv2.drawMatches(test, kp_1, target, kp_2, good_points, None)
cv2.imshow("result", result)
cv2.imshow("Original", test)
cv2.imshow("Duplicate", target)
cv2.waitKey(0)
cv2.destroyAllWindows()

# def crunch(img):
# 	planes=cv2.split(img)
# 	return (cv2.calcHist(planes,[0],None,[256],[0,256]),
# 		cv2.calcHist(planes,[1],None,[256],[0,256]),
# 		cv2.calcHist(planes,[2],None,[256],[0,256]))

# def compareCrunches(a,b):
# 	r=cv2.compareHist(a[0],b[0],cv2.HISTCMP_BHATTACHARYYA)
# 	g=cv2.compareHist(a[0],b[0],cv2.HISTCMP_BHATTACHARYYA)
# 	b=cv2.compareHist(a[0],b[0],cv2.HISTCMP_BHATTACHARYYA)
# 	return (r,g,b)


# print(compareCrunches(crunch(testTarget),crunch(target)))