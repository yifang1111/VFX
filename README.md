# VFX_hw1

## 1. Description 

藉由以不同快門速度拍攝場景，還原出 High Dynamic Range image, 描繪出 response curve 和 radiance map 表現場景的能量分佈，最後進行 tone mapping 製作出貼近電腦視覺效果的 Low Dynamic Range image.

## 2. Experiment Setup

### 相機設定


| 項目 | 描述                  |
|:---- |:--------------------- |
| 機型 | NIKON D90             |
| 鏡頭 | AF Nikkor 50mm f/1.4D |
| 焦距 | 50mm                  |
| ISO  | 200                   |
| F    | f/5                   |


### 場景圖片
| 項目   | 描述      |
|:------ |:--------- |
| 尺寸   | 2144x1424 |
| 解析度 | 300x300   |
| 數量   | 10        |

快門速度：1/4, 1/8, 1/15, 1/30, 1/60, 1/125, 1/250, 1/500, 1/1000, 1/2000

* 場景ㄧ：森林系館走廊

<img src="https://i.imgur.com/XLaETY8.jpg" width="200px"><img src="https://i.imgur.com/1JQbvj6.jpg" width="200px"><img src="https://i.imgur.com/FnKLwuM.jpg" width="200px"><img src="https://i.imgur.com/yMrpufi.jpg" width="200px"><img src="https://i.imgur.com/VZohd2R.jpg" width="200px"><img src="https://i.imgur.com/nUZw4cB.jpg" width="200px"><img src="https://i.imgur.com/49007ct.jpg" width="200px"><img src="https://i.imgur.com/t7IC58d.jpg" width="200px"><img src="https://i.imgur.com/QMlfDZv.jpg" width="200px"><img src="https://i.imgur.com/LtenHUO.jpg" width="200px">

* 場景二：森林系館草地

<img src="https://i.imgur.com/szIOumI.jpg" width="200px"><img src="https://i.imgur.com/NRMllN5.jpg" width="200px"><img src="https://i.imgur.com/OUunUAa.jpg" width="200px"><img src="https://i.imgur.com/XgIpoYx.jpg" width="200px"><img src="https://i.imgur.com/fe7pkpk.jpg" width="200px"><img src="https://i.imgur.com/rQjkIdX.jpg" width="200px"><img src="https://i.imgur.com/IOocPoe.jpg" width="200px"><img src="https://i.imgur.com/ORKWDzd.jpg" width="200px"><img src="https://i.imgur.com/nvUwIQG.jpg" width="200px"><img src="https://i.imgur.com/ReBUKsi.jpg" width="200px">

## 3. Program Workflow

1. 讀取所有在指定路徑下的十張不同快門速度的圖片。
2. 使用 MTB 做 Image Alignment。
3. 重建 HDR 影像（Debevec or Robertson）
4. 用 Tone mapping 輸出 LDR 影像（Global, Mantiuk, Drago, Durand, or Reinhard）

## 4. Implementation Detail

### MTB Alignment
**Introduction:**

**Result:**

原圖:

<img src="https://user-images.githubusercontent.com/63309875/228558197-3de1e759-e2ab-4be3-ae14-ecff34b73a73.gif" width="300"/>

做完 MTB 後，照片成功對齊:

<img src="https://user-images.githubusercontent.com/63309875/228558225-aa7d527d-e1b2-4d16-a6d9-49f317d02474.gif" width="300"/>




### HDR Algorithm
#### (a) Debevec's method

**Introduction:**

1. 挑一張圖片，對該圖片的 0-255 intensity 隨機各取一點作為 Sample $Z$，最多總共取 $P=256$ 點，並對所有 $N=10$ 張圖片都取一樣的位置。
2. 找出目標函式的最佳解。

$$O=\sum^N_{i=1}\sum^P_{j=1} \{w(Z_{i,j})[g(Z_{i,j}-\ln E_i - \ln \triangle  t_j )]\}^2 + \lambda \sum^{Z_{max}-1}_{Z_{min}+1} [w(z)g''(z)]^2 $$ 

3. 解 Sparse linear system 以找出目標函式 $O$ 的最佳解。
4. 利用解出的 Response curve $g(Z_{i,j})$，去除噪點並獲得 Radiance map. 
 
$$\ln E_i = \frac{\sum\limits_{j=1}^P w(Z_{i,j}) (g(Z_{i,j})- \ln \triangle  t_j )}{\sum\limits_{j=1}^P w(Z_{i,j})} $$



**Result:**

- Radiance Map 


<img src="https://i.imgur.com/FU2u3uW.jpg" width="400px"> <img src="https://i.imgur.com/28rKuex.jpg" width="400px">

- Response Curve:

<img  src="https://i.imgur.com/oMjyfZ5.jpg" width="400px"><img src="https://i.imgur.com/zbmIOzY.jpg" width="400px">






#### (b) Robertson's method
**Introduction:**
對 Response curve $g$ 沒有任何假設，並且取照片中所有的點作為 Sample $Z$。

給定 Sample $Z$ 和快門速度 $\triangle  t_j$，使用以下步驟求出 $E_i$ 和 $g(Z_{i,j})$：

1. 假設 $g(Z_{i,j})$ 已知，使用以下公式求出 $E_i$： $$E_i = \frac{\sum_j w(Z_{i,j})g(Z_{i,j}) \triangle  t_j }{\sum_j w(Z_{i,j})\triangle  t^2_j}$$
2. 假設 $E_i$ 已知，使用以下公式求出 $g(Z_{i,j})$：$$g(m) = \frac{1}{|E_m|} \sum_{i,j \in E_m} E_i \triangle  t_j$$ $$g(128) = 1$$
3. 重複 1. and 2. 直到數值收斂。





**Result:**


- Radiance Map 

- Response Curve:

### Tone Mapping Algorithm
我們有嘗試五種方法做比較：Global, Mantiuk, Drago, Durand, or Reinhard

1. Global

- 場景ㄧ：森林系館走廊（左圖為 Debevec, 右圖為 Robertson）
- 場景二：森林系館草地（左圖為 Debevec, 右圖為 Robertson）

2. OpenCV: Mantiuk

- 場景ㄧ：森林系館走廊（左圖為 Debevec, 右圖為 Robertson）
- 場景二：森林系館草地（左圖為 Debevec, 右圖為 Robertson）

3. OpenCV: Drago
使用OpenCV內建tone mapping的Drago method

- 場景ㄧ：森林系館走廊（左圖為 Debevec, 右圖為 Robertson）
- 場景二：森林系館草地（左圖為 Debevec, 右圖為 Robertson）

4. OpenCV: Reinhard

- 場景ㄧ：森林系館走廊（左圖為 Debevec, 右圖為 Robertson）
- 場景二：森林系館草地（左圖為 Debevec, 右圖為 Robertson）




## 6 Summary

我們完成了以下work:
- 實作 MTB algorithm
- 實作 Debevec、Robertson method
- 實作 Tone mapping 的 Global Opertor




## 7. Reproduce Steps
1. Read https://www.csie.ntu.edu.tw/~cyy/courses/vfx/23spring/assignments/proj1/
2. Know Paul Debevec's method from week 3.
3. Download sample test images from [here](http://www.mpii.mpg.de/resources/hdr/calibration/exposures.tgz) or [here](http://www.debevec.org/Research/HDR/SourceImages/Memorial_SourceImages.zip) (hdr [here](http://www.debevec.org/Research/HDR/memorial.hdr)).

4. Download our images from [here]()
5. TBD
