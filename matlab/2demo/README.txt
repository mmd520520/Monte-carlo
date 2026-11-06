并行与可调斜入射版（MATLAB R2023a）

一、直接使用
    options = struct;
    options.useParallel = true;
    options.numWorkers = 4;
    options.batchSize = 500;
    options.thetaDeg = 30;
    options.phiDeg = 0;
    options.plotBinFactor = 5;
    results = Step4_Main(2000, false, 1, true, options);
    Step10_Plot(results);

主程序第五个输入是options；原先前四个输入的含义保持不变。
options未提供时：并行true、4进程、每批5000光子、入射角0度、方位角0度。
main.m保留原来800万光子的总量，集中设置所有参数；首次验证请先减小光子数。
若运行main.m，修改其options即可，不需要改前三个原始脚本。

二、入射角定义
thetaDeg：空气中入射方向与皮肤法线+z的夹角，范围[0,90)度。
phiDeg：方位角，0朝+x，90朝+y，180朝-x。
光在皮肤内部的方向由Snell定律计算，不能直接使用空气方向。
表面镜面反射率采用非偏振Fresnel公式(Rs+Rp)/2。
Configure_ObliqueSource在原Light_T脚本执行后应用用户角度，并更新W0。
不再需要手动执行oblique_shot.m。

光斑直径沿用原定义：皮肤水平表面上的均匀圆形照射区域，默认直径1 mm。
它不是“垂直于斜光束轴的圆截面直径”；后者投影到皮肤会变成椭圆。
空气中的光柱位置按入射/反射方向反投影到皮肤圆形光斑计算。
标量光通量=法向照度/cos(theta)，并叠加空气中的MC逃逸光路径。
空气区域是有限计算窗口，斜光柱的部分路径可能在窗口以外。

三、并行实现
MC_RunBatch：各批独立累计，不共享可写数组；不画图、不保存文件。
MC_RunBatches：通过parfeval滚动提交任务，控制同时活动任务数。
只回传稀疏非零体素，按批编号合并原始吸收/逃逸/空气路径统计。
合并完后才由Step9_Output统一归一化，避免重复能量或错误加权。
model通过parallel.pool.Constant在每个进程缓存，减少重复传输。
已有池大于请求值时只提交指定数目的活动任务，不关闭用户已有池。
已有池小于numWorkers时使用现有进程数，并打印实际活动数，不自动关闭或重建池。
最多同时活动的任务=min(numWorkers,池工作进程数,批次数)。
若总光子数小于batchSize，只有一批，不会出现多批并发。
400^3模型的每个工作进程仍需约0.7GB以上数组内存，主进程另需输出内存。

四、复现和比较
随机数采用mrg32k3a，每个批编号对应一个独立子流。
固定代码、网格、光子数、seed和batchSize时，串行与并行使用相同随机样本，
且按相同批顺序合并；更改工作进程数不改变批划分及随机样本。
更改batchSize会改变随机样本。与旧twister串行版的逐像素结果不保证相同。
options.useParallel=false可以使用同样批次和子流运行串行参考结果。

五、分辨率与显示
smokeTest=false保留400^3计算网格；true为40^3粗网格测试。
plotBinFactor只控制显示，不改变results.Phi。
默认factor=5时，400^3的单层分箱图为80x80，坐标对应0.05 mm。
分箱坐标按体素中心实际计算，修正旧版本80x80数据与坐标长度不符的问题。
plotBinFactor=1只绘制原始截面；空气光柱与组织结果使用同一色标。

六、验证
    report = Test_ParallelOblique(true);
会使用121个光子、40^3网格，测试Fresnel、Snell、空气光柱几何、能量收支、
串行复现，以及2工作进程与串行累计数组的一致性。
    report = Test_ParallelOblique(false);
只进行串行及几何测试，不启动池。
此前Test_Organized保留作旧接口测试，但可能使用默认并行配置，优先运行新测试。

本次修改核验：新增/修改文件经R2023a独立代码分析器检查。
这里的MATLAB在启动阶段发生本地Access violation，未执行到用户代码；
本次不能宣称实际并行测试通过，请在当前可正常打开的MATLAB中运行上述测试。

七、保留文件与备份
Tissue.m、Tissue _optical_parameters.m、Light_T.m原样保留。
本次写回时备份目录创建命令出错，未生成本次修改前的完整逐字节快照。
reference_serial_version目录是上一份已交付的串行版参考副本，不等同本次2demo原样备份。
参考目录不要加入MATLAB搜索路径，避免旧同名函数干扰。
