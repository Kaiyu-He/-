from Client import Client
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox


def receive_msg(client, chat_boxes, user_listbox):
    """接收消息并更新对应的聊天框"""
    while True:
        try:
            data = client.read()
            if data:
                # 假设消息格式为 "发送者: 消息内容"
                sender, message = data.split(":", 1)
                if sender not in chat_boxes:
                    # 如果发送者不在用户列表中，添加到列表
                    user_listbox.insert(tk.END, sender)
                    chat_boxes[sender] = []
                # 更新对应的聊天框
                chat_boxes[sender].append(f"{sender}: {message}")
                # 如果当前聊天框是发送者的聊天框，更新显示
                if current_chat_box and selected_user.get() == sender:
                    current_chat_box.insert(tk.END, f"{sender}: {message}\n")
                    current_chat_box.see(tk.END)
        except Exception as e:
            print(f"接收消息出错: {e}")
            break


def send_msg(client, input_field, current_chat_box, selected_user):
    """发送消息"""
    msg = input_field.get()
    if msg:
        try:
            if selected_user:
                # 发送定向消息
                full_msg = f"{selected_user}: {msg}"
                client.send_msg(full_msg)
                current_chat_box.insert(tk.END, f"你向 {selected_user} 发送了：{msg}\n")
            else:
                # 发送普通消息
                client.send_msg(msg)
                current_chat_box.insert(tk.END, f"你发送了：{msg}\n")
            current_chat_box.see(tk.END)
            input_field.delete(0, tk.END)
        except Exception as e:
            print(f"发送消息出错: {e}")


def add_friend(client, user_listbox):
    """添加好友"""
    friend_name = tk.simpledialog.askstring("添加好友", "请输入好友的用户名:")
    if friend_name:
        try:
            # 发送添加好友请求
            client.send_msg(f"ADD_FRIEND:{friend_name}")
            # 等待服务器响应
            response = client.read()
            if response == "FRIEND_ADDED":
                user_listbox.insert(tk.END, friend_name)
                messagebox.showinfo("添加好友", f"成功添加 {friend_name} 为好友")
            else:
                messagebox.showerror("添加好友", f"添加好友失败: {response}")
        except Exception as e:
            messagebox.showerror("添加好友", f"添加好友出错: {e}")


def create_login_frame(root, start_chat_callback):
    """创建登录界面"""
    login_frame = tk.Frame(root)
    login_frame.pack(pady=20)

    name_label = tk.Label(login_frame, text="输入用户名：")
    name_label.pack(pady=5)
    name_entry = tk.Entry(login_frame)
    name_entry.pack(pady=5)

    # 绑定回车键事件
    name_entry.bind("<Return>", lambda event: start_chat_callback(name_entry.get()))

    start_button = tk.Button(login_frame, text="开始聊天", command=lambda: start_chat_callback(name_entry.get()))
    start_button.pack(pady=20)

    return login_frame


def create_chat_frame(root, client):
    """创建聊天界面"""
    global current_chat_box, selected_user

    chat_frame = tk.Frame(root)
    chat_frame.pack(pady=20, fill=tk.BOTH, expand=True)

    # 左侧用户选择栏
    user_frame = tk.Frame(chat_frame)
    user_frame.pack(side=tk.LEFT, fill=tk.Y)

    user_listbox = tk.Listbox(user_frame, width=20)
    user_listbox.pack(fill=tk.BOTH, expand=True)

    # 添加好友按钮
    add_friend_button = tk.Button(user_frame, text="添加好友", command=lambda: add_friend(client, user_listbox))
    add_friend_button.pack(pady=5)

    # 用于存储当前选中的用户
    selected_user = tk.StringVar()
    selected_user.set("")

    # 存储每个用户的聊天记录
    chat_boxes = {}

    # 当前显示的聊天框
    current_chat_frame = tk.Frame(chat_frame)
    current_chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    current_chat_box = scrolledtext.ScrolledText(current_chat_frame, width=50, height=20)
    current_chat_box.pack(pady=10, fill=tk.BOTH, expand=True)

    def on_user_select(event):
        """切换用户时更新聊天框"""
        selected_index = user_listbox.curselection()
        if selected_index:
            selected_user.set(user_listbox.get(selected_index))
            user = selected_user.get()
            # 清空当前聊天框
            current_chat_box.delete(1.0, tk.END)
            # 显示历史消息
            if user in chat_boxes:
                for message in chat_boxes[user]:
                    current_chat_box.insert(tk.END, f"{message}\n")
            current_chat_box.see(tk.END)

    # 绑定用户选择事件
    user_listbox.bind("<<ListboxSelect>>", on_user_select)

    # 创建输入框
    input_field = tk.Entry(chat_frame, width=40)
    input_field.pack(pady=5)

    # 绑定回车键事件
    input_field.bind("<Return>", lambda event: send_msg(client, input_field, current_chat_box, selected_user.get()))

    # 创建发送按钮
    send_button = tk.Button(chat_frame, text="发送", command=lambda: send_msg(client, input_field, current_chat_box, selected_user.get()))
    send_button.pack(pady=5)

    # 启动接收消息的线程
    receive_thread = threading.Thread(target=receive_msg, args=(client, chat_boxes, user_listbox))
    receive_thread.daemon = True
    receive_thread.start()

    return chat_frame


def main(host='10.24.19.231', port=1234):
    """主函数"""
    root = tk.Tk()
    root.title("聊天客户端")

    def start_chat(name):
        if name:
            login_frame.pack_forget()  # 隐藏登录界面
            client = Client(host, port, name)
            create_chat_frame(root, client)

    login_frame = create_login_frame(root, start_chat)
    root.mainloop()


if __name__ == "__main__":
    main()