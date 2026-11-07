%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 圆面上累计光注量的面积积分 clear;clc

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
    zq = targetZ(j)*ones(size(xq));%生成矩阵zq代表Z轴坐标

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
plot(depthsCm, Hint./(results.source.power*exposureSeconds), '^-', 'Color','y','LineWidth', 1.5);
xlabel('皮下深度 [cm]');
% ylabel('累计光注量面积积分 [J]');
ylabel(sprintf('占总能量百分比(%%)（总能量：%g J）', ...
    results.source.power * exposureSeconds));
ylim([0 0.6]);
xlim([0 8]);
title(sprintf('圆面半径 %g cm，功率 %g W，照射 %g s', ...
    circleRadiusCm, results.source.power, exposureSeconds));
xticks(depthsCm);
legend('(a)diameter:2cm','(b)diameter:4cm','(c)diameter:8cm','(d)diameter:10cm')
set(gca, 'FontName', '宋体', 'FontSize', 12);
grid on;