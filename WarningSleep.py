import cv2
import face_recognition
import pickle
import mediapipe as mp
import numpy as np
from pygame import mixer
from tkinter import *
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from scipy.spatial import distance
import time
import threading

# Khởi tạo âm thanh cảnh báo
mixer.init()
try:
    mixer.music.load("music.wav")
except Exception as e:
    print(f"Lỗi khi tải âm thanh: {e}")

# Khai báo biến toàn cục
skip_face_check = False

# Hàm tính tỷ lệ mở mắt (EAR)
def eye_aspect_ratio(eye_landmarks):
    A = distance.euclidean(eye_landmarks[1], eye_landmarks[5])
    B = distance.euclidean(eye_landmarks[2], eye_landmarks[4])
    C = distance.euclidean(eye_landmarks[0], eye_landmarks[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Hàm lưu mật khẩu vào file
def save_password(password):
    with open("password.txt", "w") as f:
        f.write(password)

# Hàm đọc mật khẩu từ file
def load_password():
    try:
        with open("password.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

# Hàm quét và lưu mã hóa khuôn mặt chủ xe từ camera
# Hàm quét và lưu mã hóa khuôn mặt chủ xe từ camera
# Hàm quét và lưu mã hóa khuôn mặt chủ xe từ camera (yêu cầu nhập mật khẩu)
def save_face_encoding():
    correct_password = load_password()  # Đọc mật khẩu đã lưu từ file
    if correct_password is None:
        messagebox.showwarning("Cảnh báo", "Chưa có mật khẩu nào được cài đặt.")
        return

    password_correct = False  # Cờ để kiểm tra mật khẩu đúng
    while not password_correct:
        entered_password = simpledialog.askstring("Nhập mật khẩu", "Vui lòng nhập mật khẩu để tiếp tục:", show='*')
        
        if entered_password is None:  # Kiểm tra nếu người dùng nhấn "Cancel"
            return  # Thoát hàm nếu người dùng không nhập mật khẩu

        if entered_password == correct_password:  # So sánh với mật khẩu đã lưu
            password_correct = True
        else:
            messagebox.showerror("Sai mật khẩu", "Mật khẩu không đúng. Vui lòng thử lại.")

    cap = cv2.VideoCapture(0)
    
    
    name = None  # Khởi tạo biến tên
    while True:  # Vòng lặp để nhập tên cho đến khi có tên hợp lệ
        name = simpledialog.askstring("Nhập tên", "Vui lòng nhập tên của người:")
        
        if name is None:  # Kiểm tra nếu người dùng nhấn "Cancel"
            return  # Thoát hàm nếu người dùng không nhập tên

        if not name.strip():  # Nếu tên trống hoặc chỉ chứa khoảng trắng
            messagebox.showwarning("Cảnh báo", "Tên không thể để trống. Vui lòng nhập lại.")
        else:
            break  # Thoát vòng lặp nếu tên hợp lệ
    face_encodings_dict = {}
    
    try:
        with open('face_encodings.pkl', 'rb') as f:
            face_encodings_dict = pickle.load(f)
    except FileNotFoundError:
        pass  # Nếu file không tồn tại, chúng ta sẽ tạo mới

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Lỗi", "Không thể mở camera.")
            break

        frame = cv2.flip(frame, 1)
        cv2.imshow("Quét khuôn mặt", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            if face_locations:
                face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                face_encodings_dict[name] = face_encoding  # Lưu mã hóa với tên
                
                with open('face_encodings.pkl', 'wb') as f:
                    pickle.dump(face_encodings_dict, f)
                    
                messagebox.showinfo("Thành công", f"Lưu thành công mã hóa khuôn mặt của {name}.")
                break
            else:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy khuôn mặt, vui lòng thử lại.")

    cap.release()
    cv2.destroyAllWindows()



# Hàm yêu cầu nhập mật khẩu
def request_password():
    password_window = Toplevel(root)
    password_window.title("Nhập mật khẩu")

    Label(password_window, text="Nhập mật khẩu:").pack(pady=10)
    password_entry = Entry(password_window, show="*")
    password_entry.pack(pady=10)

    def check_password():
        global skip_face_check  # Biến toàn cục để điều khiển kiểm tra khuôn mặt
        entered_password = password_entry.get()
        
        if not entered_password:  # Kiểm tra ô nhập mật khẩu có trống không
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mật khẩu.")
            return

        if entered_password == load_password():  # So sánh mật khẩu với mật khẩu đã lưu
            messagebox.showinfo("Thành công", "Mật khẩu chính xác. Bạn có thể sử dụng hệ thống.")
            skip_face_check = True  # Bỏ qua kiểm tra khuôn mặt
            password_window.destroy()
            recognize_face_and_sleep()  # Bắt đầu cảnh báo buồn ngủ
        else:
            messagebox.showerror("Sai mật khẩu", "Mật khẩu không đúng. Vui lòng thử lại.")
            password_entry.delete(0, END)  # Xóa ô nhập mật khẩu để người dùng nhập lại
            password_entry.focus()  # Đặt lại tiêu điểm vào ô nhập mật khẩu

    Button(password_window, text="Xác nhận", command=check_password).pack(pady=5)
    Button(password_window, text="Hủy", command=lambda: password_window.destroy()).pack(pady=5)  # Chỉ đóng cửa sổ
def setup_password():
    existing_password = load_password()
    
    if existing_password:
        while True:
            password_entry = simpledialog.askstring("Nhập mật khẩu hiện tại", "Nhập mật khẩu hiện tại để đổi mật khẩu:")
            
            if password_entry == existing_password:
                break  # Nếu mật khẩu đúng, thoát khỏi vòng lặp
            else:
                messagebox.showerror("Sai mật khẩu", "Mật khẩu không đúng. Vui lòng thử lại.")
    
    new_password = simpledialog.askstring("Đặt mật khẩu mới", "Nhập mật khẩu mới cho hệ thống:")
    
    if new_password:
        save_password(new_password)
        messagebox.showinfo("Thành công", "Mật khẩu đã được thay đổi.")
    else:
        messagebox.showwarning("Cảnh báo", "Mật khẩu không thể để trống.")

# Hàm nhận diện buồn ngủ và khuôn mặt chủ xe
def recognize_face_and_sleep():
    thresh = 0.22  # Ngưỡng EAR để kiểm tra buồn ngủ
    frame_check = 10  # Số khung hình để kiểm tra cho chủ xe
    flag = 0
    alert_started = False
    last_alert_time = 0
    need_password = False
    global skip_face_check

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)
# Kiểm tra xem file mã hóa khuôn mặt có tồn tại không
    try:
        with open('face_encodings.pkl', 'rb') as f:
            face_encodings_dict = pickle.load(f)
    except FileNotFoundError:
        messagebox.showwarning("Cảnh báo", "Chưa tìm thấy file khuôn mặt chủ xe. Vui lòng quét khuôn mặt.")
        save_face_encoding()  # Gọi hàm quét khuôn mặt
        return  # Kết thúc hàm nếu không có file
    while True:
        if need_password and not skip_face_check:
            request_password()
            if skip_face_check:
                need_password = False
                continue
            else:
                break

        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Lỗi", "Không thể mở camera.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                left_eye_landmarks = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in [33, 160, 158, 133, 153, 144]]
                right_eye_landmarks = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in [362, 385, 387, 263, 373, 380]]

                h, w, _ = frame.shape
                left_eye_landmarks = [(int(x * w), int(y * h)) for x, y in left_eye_landmarks]
                right_eye_landmarks = [(int(x * w), int(y * h)) for x, y in right_eye_landmarks]

                # Vẽ đường viền quanh mắt trái
                left_eye_points = np.array(left_eye_landmarks, dtype=np.int32)
                cv2.polylines(frame, [left_eye_points], isClosed=True, color=(0, 255, 0), thickness=2)

                # Vẽ đường viền quanh mắt phải
                right_eye_points = np.array(right_eye_landmarks, dtype=np.int32)
                cv2.polylines(frame, [right_eye_points], isClosed=True, color=(0, 255, 0), thickness=2)

                left_ear = eye_aspect_ratio(left_eye_landmarks)
                right_ear = eye_aspect_ratio(right_eye_landmarks)
                ear = (left_ear + right_ear) / 2.0

                cv2.putText(frame, f"EAR: {ear:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                if ear < thresh:
                    flag += 1
                    if flag >= frame_check and (not alert_started or time.time() - last_alert_time > 30):
                        try:
                            mixer.music.play()
                        except:
                            print("Lỗi khi phát âm thanh.")
                        alert_started = True
                        last_alert_time = time.time()
                else:
                    flag = 0
                    alert_started = False

        # Kiểm tra khuôn mặt chủ xe (bỏ qua nếu đã nhập mật khẩu)
        if not skip_face_check:
            try:
                with open('face_encodings.pkl', 'rb') as f:
                    face_encodings_dict = pickle.load(f)

                small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.3, fy=0.3)
                face_locations = face_recognition.face_locations(small_frame)
                face_encodings = face_recognition.face_encodings(small_frame, face_locations)

                face_found = False
                for face_encoding in face_encodings:
                    for name, known_face_encoding in face_encodings_dict.items():
                        print(f"Đang kiểm tra: {name}")  # In tên đang kiểm tra
                        match = face_recognition.compare_faces([known_face_encoding], face_encoding, tolerance=0.4)
                        if match[0]:
                            print(f"Nhận diện thành công: {name}")  # In tên được nhận diện
                            cv2.putText(frame, f"Chủ xe: {name}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            face_found = True
                            flag += 1
                            if flag >= frame_check:
                                flag = 0  # Nếu chủ xe được nhận diện, reset cờ của người lạ
                            break  # Thoát vòng lặp sau khi tìm thấy một khuôn mặt phù hợp

                    if face_found:
                        break  # Thoát vòng lặp bên ngoài nếu đã tìm thấy khuôn mặt

                if not face_found:
                    cv2.putText(frame, "Không hợp lệ", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    if flag == 0:  # Chỉ yêu cầu mật khẩu nếu chưa cảnh báo
                        need_password = True

            except Exception as e:
                print(f"Lỗi: {e}")



        cv2.imshow("Camera", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()



# Hàm chính
if __name__ == "__main__":
    root = Tk()
    root.title("Hệ thống nhận diện buồn ngủ")
    root.geometry("400x400")
    root.configure(bg="#f0f0f0")  # Màu nền nhẹ nhàng

    # Tiêu đề
    title_label = Label(root, text="Hệ thống nhận diện buồn ngủ", font=("Helvetica", 18, "bold"), bg="#f0f0f0", fg="#333")
    title_label.pack(pady=20)

    # Khung chứa các nút
    button_frame = Frame(root, bg="#f0f0f0")
    button_frame.pack(pady=10)

    # Hàm tạo nút với phong cách hiện đại
    def create_modern_button(text, command):
        button = Button(button_frame, text=text, command=command, 
                        width=25, height=2, bg="#4CAF50", fg="white", 
                        font=("Helvetica", 12), borderwidth=0, relief="flat")
        button.pack(pady=5)
        
        # Hiệu ứng khi rê chuột
        def on_enter(e):
            button['bg'] = "#45a049"  # Thay đổi màu nền khi rê chuột
            
        def on_leave(e):
            button['bg'] = "#4CAF50"  # Trở về màu ban đầu
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    # Nút quét khuôn mặt và lưu
    create_modern_button("Quét khuôn mặt và lưu", save_face_encoding)
    
    # Nút nhận diện khuôn mặt và kiểm tra buồn ngủ
    create_modern_button("Nhận diện và kiểm tra buồn ngủ", recognize_face_and_sleep)
    
    # Nút thiết lập mật khẩu
    create_modern_button("Thiết lập mật khẩu", setup_password)

    # Footer
    footer_label = Label(root, text="© 2024 Hệ thống nhận diện", font=("Helvetica", 10), bg="#f0f0f0", fg="#666")
    footer_label.pack(side=BOTTOM, pady=10)

    root.mainloop()