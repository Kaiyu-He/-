# 网络聊天室

## 需要实现的功能

 - [x] 用户登入
 - [x] 添加好友
 - [x] 好友间私聊
 - [ ] 群聊
 - [ ] 载入历史信息
 - [ ] 美化布局
 - [ ] 发送图片
 - [ ] 视频聊天

## 服务器反馈内容

```message:{from_user}/{to_user}/{msg}``` $\to$  ```message:{from_user}/{to_user}/{msg}```
- from_user: 发送消息的用户 
- to_user: 接受消息的用户
- msg: 聊天的内容

登入下线时 ```users_online:{user.online}```
- user.online: json格式的用户在线信息 
  - ```{name: whether_online}```