from ultralytics import YOLO

'''This file is a simple exporter script to convert trained YOLO models into ONNX format.
Functinoality:
    -Loads the trained PyTorch YOLO models (.pt files)
    -Exports them into ONNX format with a specified image size (320 in this case).
    -This is for compatibility with the computer vision node, 
    which is more optimized for inference in production environments.
 
'''

#-----------------------------------------------------------------------
# NOTE: If you want to switch out the models you're using, 
# you would retrain your new models.
#-----------------------------------------------------------------------


# 1. Export Human Tracker at 320
model_human = YOLO('2_yolo26n.pt')
model_human.export(format='onnx', imgsz=320) # <-- Forces the ONNX mold to be 320!

# 2. Export Banana Sniper at 320
model_banana = YOLO('best_a100.pt')
model_banana.export(format='onnx', imgsz=320)