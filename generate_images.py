#-*-coding:utf-8-*-
# 这是用来打开摄像头，并每隔一个固定的间隔将摄像头的图片保存下来，存储到lmdb中，并且由于大小的限制，存储的长度是有上限的，达到上限后自动清除开始的
import lmdb
import time
import math
import threading
import cv2
import os

# 删除之前的存档
os.system('rm -rf ./images')

# 打开数据库
env = lmdb.open('./images', map_size = 1073741824)
record_list = []
MAX_RECORD_LEN = 1000
lock = threading.Lock()
# 新建增添数据库的函数
def write_image(time_stamp, image):
    # 转换
    time_stamp = str(time_stamp)
    print(f'record {time_stamp}')
    image = cv2.imencode('.jpg', image)[1]
    lock.acquire()
    try:
        txn = env.begin(write = True)
        # 写入数据库
        txn.put(key = time_stamp.encode(), value = image.tobytes())
        # 写入记录列表
        record_list.append(time_stamp)
        # 列表过长时，删除开头列表
        if len(record_list) > MAX_RECORD_LEN:
            assert len(record_list) == MAX_RECORD_LEN + 1
            txn.delete(record_list[0].encode())
            print(f'delete {record_list[0]}')
            del record_list[0]
        txn.put(key = 'max'.encode(), value = time_stamp.encode())
        txn.commit()
    finally:
        lock.release()

cap = cv2.VideoCapture(0)
# time
frequency = 10.
time_stamp = math.floor(time.time() * frequency)

while True:
    next_time_stamp = time.time() * frequency
    assert next_time_stamp - time_stamp > 0 and next_time_stamp - time_stamp < 2
    while next_time_stamp - time_stamp < 1:
        time.sleep((time_stamp + 1 - next_time_stamp) / frequency)
        next_time_stamp = time.time() * frequency
        assert next_time_stamp - time_stamp > 0 and next_time_stamp - time_stamp < 2
    time_stamp = math.floor(next_time_stamp)
    ret, image = cap.read()
    assert ret
    t = threading.Thread(target = write_image, args = (time_stamp, image))
    t.start()
