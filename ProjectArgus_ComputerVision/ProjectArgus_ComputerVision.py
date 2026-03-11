import cv2
from ultralytics import YOLO

#Load model
model = YOLO("yolo26n.pt")

#Video source
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    #run inference (BGR frame is fine)
    results = model(frame,conf=0.25,verbose=False)

    #Process detections
    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue

        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        clss = boxes.cls.cpu().numpy().astype(int)

        for(x1, y1, x2, y2), conf, cls in zip(xyxy, confs, clss):
            label = f"{result.names[cls]} {conf: .2f}"

            #draw box
            cv2.rectangle(
                frame,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                (0, 255, 0),
                2,
            )

            #Draw label
            cv2.putText(
                frame,
                label,
                (int(x1), int(y1)-8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        cv2.imshow("YOLO video", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break 

cap.release()
cv2.destroyAllWindows()