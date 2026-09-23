from ._stub import StubPage


class PageDevice(StubPage):
    TITLE = "设备状态"
    DESC = "电量 / 固件版本 / 信号 / 连接详情（下一轮实现）"
    ICON = "device"