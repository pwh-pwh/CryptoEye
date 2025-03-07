# CryptoEye 加密货币价格监控

CryptoEye 是一个实时加密货币价格监控工具，提供简洁的图形界面和价格提醒功能，帮助用户实时追踪加密货币市场价格变化。

## 主要功能

- 实时监控多个加密货币价格
- 自动刷新价格数据（每5秒更新一次）
- 支持设置价格预警（高价/低价提醒）
- 系统托盘通知提醒
- 深色主题界面设计
- 支持添加/删除监控币种

## 安装说明

1. 确保已安装 Python 3.7 或更高版本
2. 安装所需依赖：

```bash
pip install ttkbootstrap aiohttp win10toast
```

## 使用方法

1. 运行程序：
```bash
python token_viewer.py
```

2. 添加监控币种：
   - 在输入框中输入代币符号（如：BTC、ETH）
   - 点击 "ADD TOKEN" 按钮或按回车键添加

3. 设置价格提醒：
   - 右键点击代币行
   - 选择"设置价格监控"
   - 输入目标价格范围

4. 其他操作：
   - 双击代币行可删除该代币
   - 勾选 "AUTO REFRESH" 开启自动刷新
   - 查看状态栏获取系统提示信息

## 依赖项

- tkinter：GUI基础库
- ttkbootstrap：美化界面主题
- aiohttp：异步HTTP请求
- win10toast：Windows系统通知

## 注意事项

- 价格数据来源于加密货币交易所API
- 推荐使用稳定的网络连接
- 价格提醒触发后会自动清除该提醒设置

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License