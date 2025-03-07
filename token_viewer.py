import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import aiohttp
import asyncio
import time
import threading
from win10toast import ToastNotifier

class TokenViewer:
    def __init__(self, root):
        self.root = root
        self.root.geometry('600x400')
        
        # 设置深色主题
        style = ttk.Style(theme='darkly')
        style.configure('Custom.TButton', font=('Consolas', 10))
        style.configure('Custom.TEntry', font=('Consolas', 10))
        
        # 创建事件循环
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()

        # 创建主框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建顶部框架
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X)
        
        # 创建折叠按钮框架
        button_frame = ttk.Frame(self.top_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10), padx=(0, 5))
        
        # 添加折叠/展开按钮
        self.is_collapsed = False
        self.toggle_button = ttk.Button(
            button_frame,
            text='▼',
            command=self.toggle_collapse,
            style='Custom.TButton',
            bootstyle='success-outline',
            width=3
        )
        self.toggle_button.pack(side=tk.RIGHT)
        
        # 创建可折叠内容框架
        self.collapsible_frame = ttk.Frame(self.top_frame)
        self.collapsible_frame.pack(fill=tk.X)
        
        # 创建标题
        title_label = ttk.Label(
            self.collapsible_frame,
            text='CRYPTOEYE MONITOR',
            font=('Consolas', 20, 'bold'),
            bootstyle='success'
        )
        title_label.pack(side=tk.LEFT, pady=(0, 20), padx=(5, 0))

        # 创建输入区域框架
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 10))

        # Token输入框和添加按钮
        self.entry = ttk.Entry(
            self.input_frame,
            width=20,
            font=('Consolas', 10),
            bootstyle='success'
        )
        self.entry.pack(side=tk.LEFT, padx=(0, 10))
        self.entry.insert(0, 'Enter token symbol')
        self.entry.bind('<FocusIn>', lambda e: self.on_entry_click())
        self.entry.bind('<FocusOut>', lambda e: self.on_focus_out())
        self.entry.bind('<Return>', lambda e: self.add_token())

        add_button = ttk.Button(
            self.input_frame,
            text='ADD TOKEN',
            command=self.add_token,
            style='Custom.TButton',
            bootstyle='success-outline'
        )
        add_button.pack(side=tk.LEFT)

        # 自动刷新选项
        self.auto_refresh = tk.BooleanVar()
        refresh_frame = ttk.Frame(self.input_frame)
        refresh_frame.pack(side=tk.RIGHT, padx=(10, 0), fill=tk.X)
        self.checkbox = ttk.Checkbutton(
            refresh_frame,
            text='AUTO REFRESH',
            variable=self.auto_refresh,
            command=self.toggle_refresh,
            bootstyle='success-round-toggle',
            width=20
        )
        self.checkbox.pack(expand=True)

        # 创建代币列表框架
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建列表视图
        columns = ('Symbol', 'Price', 'Updated')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            bootstyle='success'
        )
        
        # 绑定双击事件
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Updated':
                self.tree.column(col, width=150, anchor='center')
            else:
                self.tree.column(col, width=100, anchor='center')

        self.tree.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview,
            bootstyle='success-round'
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 添加状态栏
        self.status_var = tk.StringVar(value='System Ready')
        status_label = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            font=('Consolas', 9),
            bootstyle='success'
        )
        status_label.pack(pady=(10, 0))

        self.tokens = set()
        self.refresh_id = None
        self.price_alerts = {}
        
        # 创建右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label='设置价格监控', command=self.show_price_alert_dialog)
        self.tree.bind('<Button-3>', self.show_context_menu)

    def show_context_menu(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def show_price_alert_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        symbol = self.tree.item(selected_item[0])['values'][0]
        dialog = ttk.Toplevel(self.root)
        dialog.title(f'设置价格监控 - {symbol}')
        dialog.geometry('300x330')
        dialog.transient(self.root)
        dialog.configure(bg=self.root['bg'])
        
        # 创建主框架
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 获取当前价格监控设置
        current_alerts = self.price_alerts.get(symbol, {'high': '', 'low': ''})
        
        # 创建输入框
        ttk.Label(main_frame, text='最高价格警报:', bootstyle='success').pack(pady=10)
        high_price = ttk.Entry(main_frame, bootstyle='success')
        high_price.insert(0, str(current_alerts['high']) if current_alerts['high'] is not None else '')
        high_price.pack(pady=10)
        
        ttk.Label(main_frame, text='最低价格警报:', bootstyle='success').pack(pady=10)
        low_price = ttk.Entry(main_frame, bootstyle='success')
        low_price.insert(0, str(current_alerts['low']) if current_alerts['low'] is not None else '')
        low_price.pack(pady=10)
        
        def save_alerts():
            try:
                high = float(high_price.get()) if high_price.get() else None
                low = float(low_price.get()) if low_price.get() else None
                
                if high is not None and low is not None and high <= low:
                    messagebox.showerror('错误', '最高价格必须大于最低价格')
                    return
                    
                self.price_alerts[symbol] = {'high': high, 'low': low}
                dialog.destroy()
                self.status_var.set(f'已更新 {symbol} 的价格监控设置')
            except ValueError:
                messagebox.showerror('错误', '请输入有效的数字')
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # 添加确认和取消按钮
        ttk.Button(button_frame, text='确认', command=save_alerts, bootstyle='success-outline', width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=dialog.destroy, bootstyle='danger-outline', width=10).pack(side=tk.LEFT, padx=5)
        
        dialog.grab_set()
        dialog.focus_set()

    def on_entry_click(self):
        if self.entry.get() == 'Enter token symbol':
            self.entry.delete(0, tk.END)

    def on_focus_out(self):
        if self.entry.get() == '':
            self.entry.insert(0, 'Enter token symbol')

    def add_token(self):
        symbol = self.entry.get().upper()
        if symbol == 'ENTER TOKEN SYMBOL' or not symbol:
            messagebox.showerror('Error', 'Please enter a token symbol')
            return

        if symbol in self.tokens:
            messagebox.showwarning('Warning', f'{symbol} is already in the list')
            return

        self.tokens.add(symbol)
        self.check_price(symbol)
        self.entry.delete(0, tk.END)
        self.entry.focus_set()
        self.status_var.set(f'Added token: {symbol}')

    def remove_token(self, symbol):
        self.tokens.remove(symbol)
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == symbol:
                self.tree.delete(item)
                break
        self.update_buttons()  # 确保在移除代币后更新按钮
        self.status_var.set(f'Removed token: {symbol}')
        
    def on_double_click(self, event):
        # 获取双击的行
        item = self.tree.identify('item', event.x, event.y)
        if item:
            # 获取该行的token symbol
            symbol = self.tree.item(item)['values'][0]
            if symbol:
                self.remove_token(symbol)

    async def fetch_price(self, symbol):
        try:
            url = f'https://proxy888.deno.dev/proxy/api/v2/spot/market/tickers?symbol={symbol}USDT'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    return symbol, data['data'][0]
        except Exception as e:
            return symbol, None

    def update_buttons(self, event=None):
        # 清理所有现有按钮
        for widget in self.tree.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.destroy()

        # 只为当前存在的代币创建按钮
        for item in self.tree.get_children():
            symbol = self.tree.item(item)['values'][0]
            if symbol in self.tokens:  # 只为仍在tokens集合中的代币创建按钮
                x, y, w, h = self.tree.bbox(item, 'Action')
                if x and y:
                    remove_btn = ttk.Button(
                        self.tree,
                        text='Remove',
                        style='Custom.TButton',
                        bootstyle='danger-outline',
                        command=lambda s=symbol: self.remove_token(s)
                    )
                    remove_btn.place(x=x+w//2-30, y=y+2, width=60, height=h-4)

    def update_price_display(self, symbol, data):
        if data and 'lastPr' in data:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            current_price = float(data['lastPr'])
            
            # 检查价格警报
            if symbol in self.price_alerts:
                alerts = self.price_alerts[symbol]
                if alerts['high'] is not None and current_price >= float(alerts['high']):
                    self.show_toast_notification(f'{symbol} 价格警报', f'价格已达到或超过设定的最高价格 ${alerts["high"]}')
                    self.price_alerts[symbol] = {'high': None, 'low': None}
                elif alerts['low'] is not None and current_price <= float(alerts['low']):
                    self.show_toast_notification(f'{symbol} 价格警报', f'价格已达到或低于设定的最低价格 ${alerts["low"]}')
                    self.price_alerts[symbol] = {'high': None, 'low': None}
            
            values = (
                symbol,
                f'${current_price}',
                timestamp
            )

            existing_item = None
            for item in self.tree.get_children():
                if self.tree.item(item)['values'][0] == symbol:
                    existing_item = item
                    break

            if existing_item:
                self.tree.item(existing_item, values=values)
            else:
                self.tree.insert('', tk.END, values=values)

            self.status_var.set(f'Updated price for {symbol}')
        else:
            messagebox.showerror('Error', f'Invalid token symbol: {symbol}')
            self.tokens.remove(symbol)
            self.status_var.set(f'Error updating {symbol}')

    async def check_prices(self):
        tasks = [self.fetch_price(symbol) for symbol in self.tokens.copy()]
        results = await asyncio.gather(*tasks)
        for symbol, data in results:
            self.root.after(0, self.update_price_display, symbol, data)

    def check_price(self, symbol):
        async def update_price():
            symbol_data = await self.fetch_price(symbol)
            self.root.after(0, self.update_price_display, *symbol_data)
        asyncio.run_coroutine_threadsafe(update_price(), self.loop)

    def toggle_refresh(self):
        if self.auto_refresh.get():
            self.refresh_price()
            self.status_var.set('Auto refresh enabled')
        else:
            if self.refresh_id:
                self.root.after_cancel(self.refresh_id)
                self.refresh_id = None
            self.status_var.set('Auto refresh disabled')

    def refresh_price(self):
        for symbol in self.tokens.copy():
            self.check_price(symbol)
        if self.auto_refresh.get():
            self.refresh_id = self.root.after(5000, self.refresh_price)

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def show_toast_notification(self, title, message):
        try:
            # 创建通知器实例
            toaster = ToastNotifier()
            # 显示通知
            toaster.show_toast(
                title,
                message,
                duration=5,
                threaded=True
            )
        except Exception as e:
            # 如果系统通知失败，回退到messagebox
            messagebox.showwarning(title, message)

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.collapsible_frame.pack_forget()
            self.input_frame.pack_forget()
            self.toggle_button.configure(text='▲')
        else:
            # 确保按照初始化时相同的顺序显示组件
            self.collapsible_frame.pack(fill=tk.X)
            self.input_frame.pack(fill=tk.X, pady=(0, 10), after=self.collapsible_frame)
            self.toggle_button.configure(text='▼')
            
    def __del__(self):
        self.loop.stop()
        self.loop.close()

if __name__ == '__main__':
    root = ttk.Window(
        title='CryptoEye',
        themename='darkly',
        size=(600, 400)
    )
    # 设置窗口在屏幕中央
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 600) // 2
    y = (screen_height - 400) // 2
    root.geometry(f'600x400+{x}+{y}')
    
    app = TokenViewer(root)
    root.mainloop()