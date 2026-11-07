简约版膝部蒙特卡洛程序

本目录仅整理4demo当前运行所需的22个.m文件；计算代码保持原样。
原4demo目录不修改。不包含旧皮肤血管模型、历史MAT结果、图片、备份和旧测试。

运行：将MATLAB当前目录切换到5demo，运行main。
main.m保留原有1000光子、8个并行工作进程配置；没有并行工具箱可将options.useParallel改为false。
main.m末尾原有close all会关闭图窗，结果图片仍会保存。

参数入口：
main.m：光子数、并行配置、入射角和绘图分箱。
Tissue_knee.m：几何轮廓、髌骨位置和大小，单位cm。
Tissue _optical_parameters.m：波长、吸收、约化散射、g、n及文献出处。
Light_T.m：光斑直径2.5cm、半径1.25cm、照度0.1W/cm²，总功率约0.4909W。

调用关系：
main -> Step4_Main
  -> MC_Settings
  -> Prepare_Inputs -> Tissue_knee / Tissue _optical_parameters / Light_T
  -> Configure_ObliqueSource
  -> MC_RunBatches -> MC_RunBatch -> MC_CreateTallies / Step4_Launch
      -> Step5_Hop -> Step7_Drop / Step6_Boundary
      -> Step8_SpinCheck
    -> MC_MergeTallies
  -> Step9_Output -> AddIncidentAirBeam
main -> Step10_Plot -> PlotIncidentAirBeam

Plot_Tissue3D供Tissue_knee单独运行或手动查看三维模型使用：
Plot_Tissue3D(results)

输出：运行后在本目录生成knee_mc_results.mat及knee_光子数_fluence系列PNG。
已有结果可使用：
load('knee_mc_results.mat','results');
Step10_Plot(results);
Plot_Tissue3D(results);

光学参数为文献代理及波长插值；g=0.9、n=1.4为假设。原文献说明另附。
