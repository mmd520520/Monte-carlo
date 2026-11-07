% 参数入口：修改这里即可，不必修改前三个原脚本。
clear;
clc;

photonCount = 50;             % 先验证时可改为2000或10000
options = struct;
options.useParallel = true;
options.numWorkers = 8;        % 当前配置最多10个；按内存情况选择
% delete(gcp('nocreate'));
% pool = parpool('local', 5);
options.batchSize = 1000;      % 每批光子数；小于等于总光子数
options.thetaDeg = 0;         % 空气入射角，0 <= thetaDeg < 90
options.phiDeg = 0;            % 0朝+x倾斜；90朝+y；180朝-x
options.plotBinFactor = 2;     % 仅绘图分箱；1表示不分箱
fprintf('开始\n');
tic
results = Step4_Main(photonCount, false, 1, true, options);
toc
Step10_Plot(results);
close all

