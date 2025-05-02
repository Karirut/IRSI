import cv2
import numpy as np

#KALMAN

#kalman = cv2.KalmanFilter(4, 2)
#kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
#kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
#kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03

#KALMAN CON VELOCIDADES x Y y
kalman = cv2.KalmanFilter(6, 2)
kalman.measurementMatrix = np.array([[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0]], np.float32)
kalman.transitionMatrix = np.array([[1, 0, 1, 0, 0.5, 0], [0, 1, 0, 1, 0, 0.5], [0, 0, 1, 0, 1, 0], [0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]], np.float32)
kalman.processNoiseCov = np.array([[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]], np.float32) * 0.03
#kalman.processNoiseCov = np.eye(6, dtype=np.float32)

#VIDEO
cap = cv2.VideoCapture("imag/globito_moving.mp4")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    #GRAY
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #FILTRO GAUSSIANO
    gau_img = cv2.GaussianBlur(gray, (9, 9), 0)

    #CANNY
    bordes = cv2.Canny(gau_img, 10, 200)

    #CONTORNO
    contours, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(len(contours))
    contornom = len(contours)

    #AREA
    min_area = 1  # Área mínima
    max_area = 15  # Área máxima

    cv2.imshow("cannied", bordes)

    if contours:
        for contour in contours:
            area = cv2.contourArea(contour)

            if (min_area < area < max_area):
                xm, ym, wm, hm = cv2.boundingRect(contour)

                measurementm = np.array([[np.float32(xm + wm / 2)], [np.float32(ym + hm / 2)]])
                kalman.correct(measurementm)

                predictionm = kalman.predict()
                pred_xm, pred_ym = int(predictionm[0]), int(predictionm[1])

                #DRAW PREDICTION
                cv2.circle(frame, (pred_xm, pred_ym), 5, (0, 0, 255), -1)

                #ENCUADRE
                cv2.rectangle(frame, (xm, ym), (xm + wm, ym + hm), (0, 255, 0), 2)

        #CONTORNO LARGO
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        #MEDICION KALMAN
        measurement = np.array([[np.float32(x + w / 2)], [np.float32(y + h / 2)]])
        kalman.correct(measurement)

        #PREDICCION
        prediction = kalman.predict()
        pred_x, pred_y = int(prediction[0]), int(prediction[1])

        #DRAW PREDICTION
        cv2.circle(frame, (pred_x, pred_y), 5, (0, 0, 255), -1)

        #ENCUADRE
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()