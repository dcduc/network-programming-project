> Nhóm 5:
>
> - Đinh Công Đức - 22520262
> - Nguyễn Viết Duy - 22520336
> - Vũ Tiến Giáp - 22520367

| STT | Tiêu chí                 | Điểm số khi báo cáo | Bổ sung |
| :-: | ------------------------ | :-----------------: | :-----: |
|  1  | App logic + Socket logic |          3          |    x    |
|  2  | I/O (File, Network,...)  |         0.5         |         |
|  3  | Database                 |         0.5         |         |
|  4  | Thread                   |         0.5         |         |
|  5  | Sign up/Sign in          |         0.3         |    x    |
|  6  | Multi Client             |          0          |         |
|  7  | Multi Server             |          0          |    x    |
|  8  | Cryptography             |         0.5         |         |
|  9  | Demo via LAN             |         0.5         |         |
| 10  | Demo via Internet        |         0.5         |         |
| 11  | Load balancing           |          0          |    x    |

## Chi tiết bổ sung (final version)

> Vì các tính năng tương tác với nhau nên video record em xin gộp lại làm 1 _(Đã có phụ đề đầy đủ)_.

### App logic + Socket logic

- Bổ sung tính năng shutdown và screenshot.

### Sign up/Sign in

- Bổ sung tính năng đăng nhập, đăng ký và lưu access log của client _(Trong log sẽ bao gồm thời gian kết nối, mac address của server và id client)_.

### Load balancing

- Ý tưởng ở đây là với mỗi vps handle forward connection từ server ra internet sẽ tăng `connections` của vps thêm 1. Server sẽ tìm vps đang handle ít connection nhất để forward connection ra internet. ![](https://i.imgur.com/H3dH1h4.png)
  - Sau khi server nhận kết nối từ client sẽ tăng connection lên 1 ![](https://i.imgur.com/KnNP0fB.png)
  - Client khi disconnect thì số connection của vps sẽ giảm đi 1 ![](https://i.imgur.com/ukfvZ0y.png)

### Multi Server

![](https://i.imgur.com/4eqVxaq.png)

- Trong mô hình sử dụng TCP connection kết hợp với nhiều server như trên hình vẽ.
