% 参数入口：修改这里即可，不必修改前三个原脚本。
clear;
clc;

photonCount = 100000;             % 先验证时可改为2000或10000
options = struct;
options.useParallel = true;
options.numWorkers = 8;        % 当前配置最多10个；按内存情况选择
% delete(gcp('nocreate'));
% pool = parpool('local', 5);
options.batchSize = 100;      % 每批光子数；小于等于总光子数
options.thetaDeg = 0;         % 空气入射角，0 <= thetaDeg < 90
options.phiDeg = 0;            % 0朝+x倾斜；90朝+y；180朝-x
options.plotBinFactor = 2;     % 仅绘图分箱；1表示不分箱
fprintf('开始\n');
tic
results = Step4_Main(photonCount, false, 1, true, options);
toc
Step10_Plot(results);

%%
% 探测深度和照射时间
depthsCm=[1 2 4 8];    % 距中心皮肤表面的深度，cm
exposureSeconds=300;    % 照射时间，s

% 找到最接近中心轴的体素列
[~,ix]=min(abs(results.x));
[~,iy]=min(abs(results.y));

% 找到该列第一个组织体素，确定皮肤表面位置
iz=find(squeeze(results.tissueLabels(ix,iy,:))>1,1);
dz=results.z(2)-results.z(1);
skinZ=results.z(iz)-dz/2;

% 计算各探测点的实际z坐标
targetZ=skinZ+depthsCm;

% 提取中心轴光通量率，换算累计光注量
H=zeros(size(depthsCm));

for j=1:numel(depthsCm)
    phi=interpn(results.x,results.y,results.z, ...
        results.fluenceWcm2,0,0,targetZ(j),'linear');

    H(j)=phi*exposureSeconds;    % J/cm^2
end

% 显示结果
% disp(table(depthsCm(:),targetZ(:),H(:), ...
%     'VariableNames',{'DepthBelowSkin_cm','Z_cm','H_Jcm2'}));
% 画出各深度的累计光注量
figure;
plot(depthsCm,H,'o-','LineWidth',1.5);
xlabel('皮下深度 [cm]');
ylabel('累计光注量 H [J/cm^2]');
title(sprintf('功率 %g W，光斑直径 %g cm，照射 %g s', ...
    results.source.power,results.source.diameter,exposureSeconds));
xticks(depthsCm);
grid on;



close all
% Plot_Tissue3D(results)

% report=Compare_SpotSize1([1 2 5 10],10000,2,[],false);






% 探测深度、照射时间和圆面半径
depthsCm = [1 2 3 10];   % 距中心轴皮肤表面的深度，cm
exposureSeconds = 300;   % 照射时间，s
circleRadiusCm = 1;      % 圆面半径，cm，可修改

% 找到最接近中心轴的体素列，用于确定皮肤表面
[~,ix] = min(abs(results.x));
[~,iy] = min(abs(results.y));

iz = find(squeeze(results.tissueLabels(ix,iy,:)) > 1, 1);
dz = results.z(2)-results.z(1);
skinZ = results.z(iz)-dz/2;

% 各圆面所在的实际 z 坐标
targetZ = skinZ+depthsCm;

% 在 x-y 平面建立网格，选出以原点为圆心的圆面
[X,Y] = ndgrid(results.x, results.y);
circleMask = X.^2+Y.^2 <= circleRadiusCm^2;
assert(any(circleMask(:)), '圆面半径太小，没有选中采样点。');

% 圆面内各采样点的 x、y 坐标
xq = X(circleMask);
yq = Y(circleMask);

Hmean = zeros(size(depthsCm));

for j = 1:numel(depthsCm)
    zq = targetZ(j)*ones(size(xq));

    % 提取该深度圆面内各点的光通量率，W/cm²
    phi = interpn(results.x, results.y, results.z, ...
        results.fluenceWcm2, xq, yq, zq, 'linear');

    assert(all(isfinite(phi)), '圆面采样点超出计算区域。');

    % 检查圆面采样点是否落在组织内
    labels = interpn(results.x, results.y, results.z, ...
        double(results.tissueLabels), xq, yq, zq, 'nearest');

    if any(labels == 1)
        warning('皮下 %g cm 的圆面有采样点位于空气中，均值包含这些点。', ...
            depthsCm(j));
    end

    % 圆面平均累计光注量，J/cm²
    Hmean(j) = mean(phi)*exposureSeconds;
end

% 显示结果
disp(table(depthsCm(:), targetZ(:), Hmean(:), ...
    'VariableNames', ...
    {'DepthBelowSkin_cm','Z_cm','MeanH_Jcm2'}));

% 绘图
figure;
plot(depthsCm, Hmean, 'o-', 'LineWidth', 1.5);
xlabel('皮下深度 [cm]');
ylabel('圆面平均累计光注量 [J/cm^2]');
title(sprintf('圆面半径 %g cm，功率 %g W，照射 %g s', ...
    circleRadiusCm, results.source.power, exposureSeconds));
xticks(depthsCm);
grid on;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 圆面上累计光注量的面积积分

depthsCm = [1 2 4 8];   % 距中心轴皮肤表面的深度，cm
exposureSeconds = 300;   % 照射时间，s
circleRadiusCm = 2;      % 圆面半径，cm

% 找到最接近中心轴的体素列，确定皮肤表面
[~,ix] = min(abs(results.x));
[~,iy] = min(abs(results.y));

iz = find(squeeze(results.tissueLabels(ix,iy,:)) > 1, 1);
assert(~isempty(iz), '中心轴上没有找到组织。');

dz = results.z(2)-results.z(1);
skinZ = results.z(iz)-dz/2;

% 各圆面的实际 z 坐标
targetZ = skinZ+depthsCm;

% 检查圆面范围
validateattributes(circleRadiusCm, {'numeric'}, ...
    {'scalar','real','positive','finite'});

assert(circleRadiusCm <= min([ ...
    -min(results.x), max(results.x), ...
    -min(results.y), max(results.y)]), ...
    '圆面超出可插值的 x-y 范围。');

assert(all(targetZ >= min(results.z) & ...
           targetZ <= max(results.z)), ...
    '探测深度超出可插值的 z 范围。');

% 建立 x-y 网格，选取以原点为圆心的圆面采样点
[X,Y] = ndgrid(results.x, results.y);
circleMask = X.^2+Y.^2 <= circleRadiusCm^2;

assert(any(circleMask(:)), ...
    '圆面半径太小，没有选中采样点。');

xq = X(circleMask);
yq = Y(circleMask);

circleArea = pi*circleRadiusCm^2;  % 圆面积，cm²
Hint = zeros(size(depthsCm));     % 面积积分，J

for j = 1:numel(depthsCm)
    zq = targetZ(j)*ones(size(xq));

    % 圆面各采样点的光通量率，W/cm²
    phi = interpn(results.x, results.y, results.z, ...
        results.fluenceWcm2, xq, yq, zq, 'linear');

    assert(all(isfinite(phi)), ...
        '圆面采样结果包含无效值。');

    % 检查圆面是否有采样点落在空气中
    labels = interpn(results.x, results.y, results.z, ...
        double(results.tissueLabels), ...
        xq, yq, zq, 'nearest');

    if any(labels == 1)
        warning(['皮下 %g cm 的圆面有采样点位于空气中，' ...
                 '积分包含这些点。'], depthsCm(j));
    end

    % 累计光注量的面积积分：
    % (W/cm²) × s × cm² = J
    Hint(j) = mean(phi)*exposureSeconds*circleArea;
end

% 显示结果
disp(table(depthsCm(:), targetZ(:), Hint(:)./(results.source.power*exposureSeconds), ...
    'VariableNames', ...
    {'DepthBelowSkin_cm','Z_cm','IntegratedH_J'}));

% 绘图
% figure;
hold on
plot(depthsCm, Hint./(results.source.power*exposureSeconds), 's-', 'Color','yellow','LineWidth', 1.5);
xlabel('皮下深度 [cm]');
% ylabel('累计光注量面积积分 [J]');
ylabel(sprintf('占总能量百分比（总能量：%g J）', ...
    results.source.power * exposureSeconds));
ylim([0 0.5]);
xlim([0 8]);
title(sprintf('圆面直径 %g cm，功率 %g W，照射 %g s', ...
    circleRadiusCm*2, results.source.power, exposureSeconds));
xticks(depthsCm);
legend('(a)diameter:2cm','(b)diameter:5cm','(c)diameter:8cm','(d)diameter:10cm')
set(gca, 'FontName', '宋体', 'FontSize', 12);
grid on;