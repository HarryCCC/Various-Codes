// pages/index/index.js
Page({
  data: {
    herbalList: [
      {
        id: 1,
        name: "薄荷 (Mint)",
        desc: "清凉解表，提神醒脑。",
        // 修改点：这里换成了本地路径
        image: "/images/mint.png", 
        detail: "薄荷是唇形科植物，具有清凉的香气，常用于泡茶或作为烹饪点缀。性凉，归肺、肝经。"
      },
      {
        id: 2,
        name: "迷迭香 (Rosemary)",
        desc: "香气浓郁，增强记忆。",
        // 修改点：本地路径
        image: "/images/rosemary.png",
        detail: "迷迭香是一种常绿灌木，叶片针状。在西餐中常用于牛排调味，也具有抗氧化、提神的功效。"
      },
      {
        id: 3,
        name: "枸杞 (Goji Berry)",
        desc: "滋补肝肾，益精明目。",
        // 修改点：本地路径
        image: "/images/goji.png",
        detail: "枸杞是传统中药材，富含胡萝卜素和维生素。无论是泡水还是煲汤，都是养生首选。"
      }
    ]
  },

  goToDetail(e) {
    const item = e.currentTarget.dataset.item;
    const itemStr = JSON.stringify(item);
    wx.navigateTo({
      url: `/pages/logs/logs?data=${encodeURIComponent(itemStr)}`
    })
  }
})