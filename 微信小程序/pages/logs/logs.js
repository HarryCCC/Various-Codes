// pages/logs/logs.js -> 现在的详情页
Page({
  data: {
    item: {}
  },
  onLoad(options) {
    if (options.data) {
      const item = JSON.parse(decodeURIComponent(options.data));
      this.setData({ item });
      // 动态设置标题
      wx.setNavigationBarTitle({ title: item.name });
    }
  }
})