import cv2

input_image = cv2.imread("./test4.jpg")

# resize成长宽的一半
cv2.imwrite(
    "./test4_resized_half.jpg",
    cv2.resize(input_image, (input_image.shape[1] // 2, input_image.shape[0] // 2)),
)
