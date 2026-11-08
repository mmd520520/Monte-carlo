**一句话**：本工具用的是**体素化蒙特卡洛光子包追踪**（voxel-based Monte Carlo photon-packet transport）。组织被切成小立方体（体素 voxel），每个体素有自己的吸收系数 μa、散射系数 μs、各向异性 g 和折射率 n；大量“光子包”一个一个随机地走一步、在路上留下能量、再换方向，最后统计出光注量（fluence）、吸收和反射 / 透射。

- **来历**：MCML（Wang、Jacques、Zheng，1995）建立了这套方法，mcxyz（Jacques）把它推广到三维体素。马孟帝最早用 MATLAB 写了这个程序，后来一比一移植成 Python + Numba（`mcsim/kernel.py`），结果和 MATLAB 版在统计误差内一致，并用独立的加倍法（adding-doubling）验证。
- **有没有用 GPU**：**现在没有**。网页和命令行全部在 CPU 多核上运行（Numba 把 Python 编译成机器码，多线程并行）。GPU 只做过一次可行性测试：同一个平板算例，MCX-CL 在 Apple M4 Pro 的 GPU 上 0.4 秒，我们的引擎在 14 核 CPU 上 4.8 秒，结果一致。GPU 加速的原理、和 CPU 版的区别、为什么暂缓，见“并行与 GPU”。

下面四个标签页：算法流程图、关键公式、并行与 GPU、优化方向。
