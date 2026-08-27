# 得意桌宠

一个不依赖 Codex 的 macOS 透明桌面宠物原型。初始作者为 @617，已获全量授权！

## 运行

双击 `run.command`，或在终端运行：

```sh
cd /Users/fancy/Documents/Codex/2026-08-24/hatch-pet-users-fancy-codex-skills/outputs/desktop-cat-pet
python3 slice_assets.py
python3 desktop_cat.py
```
macOS用户可直接在页面右侧【Releases】中下载已编译好的APP
win版本待更新


## 操作

- 拖动猫：移动桌宠位置
- 双击猫：打开互动菜单
- `Esc`：退出

## 状态

- 饱腹值会随时间下降
- 体力会随时间下降
- 低饱腹会影响心情
- 喂饭、摸摸、逗猫、睡觉会改变状态

状态会保存在 `cat_state.json`。
