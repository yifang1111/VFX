
# VFX_hw1

## 1. Description 

藉由以不同快門速度拍攝場景，還原出 High Dynamic Range image, 描繪出 response curve 和 radiance map 表示場景的能量分佈，最後進行 tone mapping 製作出貼近電腦視覺效果的 Low Dynamic Range image.

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
4. 用 Tone mapping 輸出 LDR 影像（Global, Mantiuk, Drago, or Reinhard）

## 4. Implementation Detail

我們實做了兩種方法：Debevec 和 Robertson.

### **(1) MTB Alignment （加分）**
**Introduction:**
1. 先將圖片轉成灰階
2. 取第一張圖片作為校正參考點，每次取兩張照片依序做 alignment
3. 使用 multiscale 的方式，將圖片縮小為 1/32，根據 x 方向 ±1 及 y 方向 ±1，做九個方向的 shift，依以下方法找出兩張圖片差異最小的 shift 方向
   - 計算 threshold bitmap，以灰階影像的 median 值為 threshold，大於為1，小於為0
   - 計算 exclusion bitmap，為了去除 noise，在灰階影像 median 值 ±4 的位置設為 0，其餘為 1
   - 透過固定一張圖片與另一張 shift 的圖片，兩者 threshold bitmap 做 XOR 計算，再與兩者的 exclusion bitmap 做AND計算，Bit counting出兩者之間的差異。
4. 每次 scale up by 2，再依前一個 scale 找出的 shift，做新的九個方向的 shift
5. 找到原圖尺寸的 shift，並且做 crop，完成 alignment.
 

**Result:**

原圖:

<img src="https://user-images.githubusercontent.com/63309875/228558197-3de1e759-e2ab-4be3-ae14-ecff34b73a73.gif" width="300"/> <img src="https://user-images.githubusercontent.com/63309875/228779198-71e27456-cddb-4d7b-9d7e-cb6b565ba482.gif" width="300"/>


做完 MTB 後，照片成功對齊:

<img src="https://user-images.githubusercontent.com/63309875/228558225-aa7d527d-e1b2-4d16-a6d9-49f317d02474.gif" width="300"/> <img src="https://user-images.githubusercontent.com/63309875/228779249-7df876e7-da3a-4ab6-a3ef-039ad7d8ea1d.gif" width="300"/>


____________________________________________________________
### (2) HDR Algorithm
#### (a) Debevec's method

**Introduction:**

1. 挑一張圖片，對該圖片的 0-255 intensity 隨機各取一點作為 Sample $Z$，最多總共取 $P=256$ 點，並對所有 $N=10$ 張圖片都取一樣的位置。
2. 找出目標函式的最佳解。

$$O=\sum^N_{i=1}\sum^P_{j=1} \{w(Z_{i,j})[g(Z_{i,j}-\ln E_i - \ln \triangle  t_j )]\}^2 + \lambda \sum^{Z_{max}-1}_{Z_{min}+1} [w(z)g''(z)]^2 $$ 

3. 解 Sparse linear system 以找出目標函式 $O$ 的最佳解。
4. 利用解出的 Response curve $g(Z_{i,j})$，去除噪點並獲得 Radiance map. 
 
$$\ln E_i = \frac{\sum\limits_{j=1}^P w(Z_{i,j}) (g(Z_{i,j})- \ln \triangle  t_j )}{\sum\limits_{j=1}^P w(Z_{i,j})} $$



**Result:**

- Radiance Map:

<img src="https://i.imgur.com/vTAlhEP.jpg" width="400px"> <img src="https://i.imgur.com/jyguD0c.jpg" width="400px"> 

- Response Curve:

<img src="https://i.imgur.com/zbmIOzY.jpg" width="400px"> <img src="https://i.imgur.com/oMjyfZ5.jpg" width="400px"> 



#### **(b) Robertson's method （加分）**
**Introduction:**
對 Response curve $g$ 沒有任何假設，並且取照片中所有的點作為 Sample $Z$。

給定 Sample $Z$ 和快門速度 $\triangle  t_j$，使用以下步驟求出 $E_i$ 和 $g(Z_{i,j})$：

1. 假設 $g(Z_{i,j})$ 已知，使用以下公式求出 $E_i$：
$$E_i = \frac{\sum_j w(Z_{i,j})g(Z_{i,j}) \triangle  t_j }{\sum_j w(Z_{i,j})\triangle  t^2_j}$$
2. 假設 $E_i$ 已知，使用以下公式求出 $g(Z_{i,j})$：
$$g(m) = \frac{1}{|E_m|} \sum_{i,j \in E_m} E_i \triangle  t_j$$ $$g(128) = 1$$
3. 重複 1. and 2. 直到數值收斂。



**Result:**

- Radiance Map:

<img src="https://i.imgur.com/EKFDOyM.jpg" width="400px"> <img src="https://i.imgur.com/RxrGTv9.jpg" width="400px"> 

- Response Curve:

<img src="https://i.imgur.com/5tauvhy.jpg" width="400px"> <img src="https://i.imgur.com/QSWTr2q.jpg" width="400px"> 

____________________________________________________________
### (3) Tone Mapping Algorithm 
我們有實作 Global Tone Mapping, 並與其他三種方法做比較：Mantiuk, Drago, or Reinhard.

**1. Global Operator （加分）**

使用以下公式把 HDR Intensity $L_w$ 調整成 LDR Intensity $L_d$:

$$L_d(x,y) = \frac{ L_m(x,y)(1+\frac{L_m(x,y)}{L^2_{white}(x,y)}) }{1+L_m(x,y)}  $$

$$L_m(x,y) = \frac{a}{\bar{L}_w} L_w(x,y)$$

$$\bar{L}_w = exp(\frac{1}{N} \sum\limits_{x, y}\log(\delta+ L_w(x, y) )  $$


$a=0.9$, $L_{white}=4.0$, $\delta=0.0000001$ 

- 場景ㄧ：森林系館走廊（左圖為 Debevec , 右圖為 Robertson）

<img src="https://i.imgur.com/aOU09zv.jpg" width="400px"> <img src="https://i.imgur.com/jInrsqw.jpg" width="400px">


- 場景ㄧ：森林系館草地（左圖為 Debevec , 右圖為 Robertson）

<img src="https://i.imgur.com/pdvcera.jpg" width="400px"> <img src="https://i.imgur.com/EI5T9vo.jpg" width="400px">

(b) OpenCV: Mantiuk

- 場景ㄧ：森林系館走廊（左圖為 Debevec Mantiuk, 右圖為 Robertson Mantiuk ）

<img src="https://i.imgur.com/QvkwxYF.jpg" width="400px"> <img src="https://i.imgur.com/bnrH0wQ.jpg" width="400px">


- 場景二：森林系館草地（左圖為 Debevec Mantiuk, 右圖為 Robertson Mantiuk）

<img src="https://i.imgur.com/C8dd9mM.jpg" width="400px"> <img src="https://i.imgur.com/UUUALLK.jpg" width="400px">

(c) OpenCV: Drago

- 場景ㄧ：森林系館走廊（左圖為 Debevec Drago, 右圖為 Robertson Drago）



<img src="https://i.imgur.com/R8Xn1Fg.jpg" width="400px"> <img src="https://i.imgur.com/3dGbDjZ.jpg" width="400px">

- 場景二：森林系館草地（左圖為 Debevec Drago, 右圖為 Robertson Drago）


<img src="https://i.imgur.com/5cfrlDq.jpg" width="400px"> <img src="https://i.imgur.com/LaRfTek.jpg" width="400px">



(d) OpenCV: Reinhard

- 場景ㄧ：森林系館走廊（左圖為 Debevec Reinhard, 右圖為 Robertson Reinhard）


<img src="https://i.imgur.com/sC3ZZUY.jpg" width="400px"> <img src="https://i.imgur.com/06nMKS5.jpg" width="400px">


- 場景二：森林系館草地（左圖為 Debevec Reinhard, 右圖為 Robertson Reinhard）

<img src="https://i.imgur.com/vO4sgVi.jpg" width="400px"> <img src="https://i.imgur.com/QiRHABN.jpg" width="400px">

**比較：**

| Method | Global | Mantiuk | Drago | Reinhard |
| --------| -------- | -------- | -------- | -------- |
| Debevec | <img src="https://i.imgur.com/aOU09zv.jpg" alt="" width="150">  | <img src="https://i.imgur.com/QvkwxYF.jpg" alt="" width="150">  | <img src="https://i.imgur.com/R8Xn1Fg.jpg" alt="" width="150">  | <img src="https://i.imgur.com/sC3ZZUY.jpg" alt="" width="150">    |
| Robertson | <img src="https://i.imgur.com/jInrsqw.jpg" alt="" width="150">  | <img src="https://i.imgur.com/bnrH0wQ.jpg" alt="" width="150">  | <img src="https://i.imgur.com/3dGbDjZ.jpg" alt="" width="150">  | <img src="https://i.imgur.com/06nMKS5.jpg" alt="" width="150">    |


| Method | Global | Mantiuk | Drago | Reinhard |
| -------- | -------- | -------- | -------- | -------- |
| Debevec  | <img src="https://i.imgur.com/pdvcera.jpg" alt="" width="150">  | <img src="https://i.imgur.com/C8dd9mM.jpg" alt="" width="150">  | <img src="https://i.imgur.com/5cfrlDq.jpg" alt="" width="150">  | <img src="https://i.imgur.com/vO4sgVi.jpg" alt="" width="150">    |
| Robertson | <img src="https://i.imgur.com/EI5T9vo.jpg" alt="" width="150">  | <img src="https://i.imgur.com/UUUALLK.jpg" alt="" width="150">  | <img src="https://i.imgur.com/LaRfTek.jpg" alt="" width="150">  | <img src="https://i.imgur.com/QiRHABN.jpg" alt="" width="150">    |


## 6. Summary

我們完成了以下work:
- **（加分）** 實作 MTB algorithm
- 實作 Debevec method
- **（加分）** 實作 Robertson method 
- **（加分）** 實作 Tone mapping 的 Global Opertor


**原圖 (左) vs 最後成果（右）：**

使用 Debevec + Global Tone Mapping 後，可以看到走廊盡頭的暗部，經過 Tone mapping 後細節與輪廓有被增強。

<img src="https://i.imgur.com/VZohd2R.jpg" width="400px"> <img src="https://i.imgur.com/aOU09zv.jpg" width="400px"> 
 
**原圖 (左) vs 最後成果（右）：**

使用 Robertson + Mantiuk Tone Mapping 後，可以看到原本過曝的薯條玩偶，經過 Tone mapping 後細節與輪廓有被增強。

<img src="https://i.imgur.com/fe7pkpk.jpg" width="400px"> <img src="https://i.imgur.com/UUUALLK.jpg" width="400px">



## 7. Reproduce Steps
1. Read https://www.csie.ntu.edu.tw/~cyy/courses/vfx/23spring/assignments/proj1/
2. Know Paul Debevec's method from week 3.
3. Download our images from [here]()
