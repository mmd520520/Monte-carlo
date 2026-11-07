%% 指定深度薄圆柱区域的吸收能量clear;clc;

depthsCm = [1 2 4 8];    % 皮下深度，cm
exposureSeconds = 300;    % 照射时间，s
circleRadiusCm = 2;       % 圆面半径，cm

% 确定中心轴皮肤表面
[~,ix] = min(abs(results.x));
[~,iy] = min(abs(results.y));

iz = find(squeeze(results.tissueLabels(ix,iy,:)) > 1, 1);
assert(~isempty(iz), '中心轴上没有找到组织。');

dx = results.x(2)-results.x(1);
dy = results.y(2)-results.y(1);
dz = results.z(2)-results.z(1);

skinZ = results.z(iz)-dz/2;
targetZ = skinZ+depthsCm;

% 检查目标位置和圆面范围
assert(all(targetZ >= min(results.z) & ...
           targetZ <= max(results.z)), ...
    '目标深度超出范围。');

assert(circleRadiusCm > 0 && ...
    circleRadiusCm <= min([-min(results.x), max(results.x), ...
                           -min(results.y), max(results.y)]), ...
    '圆面半径无效或超出范围。');

% 按体素中心选取圆形区域
[X,Y] = ndgrid(results.x, results.y);
circleMask = X.^2+Y.^2 <= circleRadiusCm^2;
assert(any(circleMask(:)), '圆面内没有采样体素。');

voxelVolume = dx*dy*dz;
inputEnergy = results.source.power*exposureSeconds;

absorbedEnergy = zeros(size(depthsCm));
absorbedPercent = zeros(size(depthsCm));
actualDepthCm = zeros(size(depthsCm));

for j = 1:numel(depthsCm)
    % 选择距目标深度最近的一层体素
    [~,kz] = min(abs(results.z-targetZ(j)));
    actualDepthCm(j) = results.z(kz)-skinZ;

    % 该层中的组织区域，排除空气
    labels = results.tissueLabels(:,:,kz);
    mask = circleMask & labels > 1;

    % 累加所选体素的归一化吸收量
    Aplane = results.A(:,:,kz);
    absorbedFraction = sum(Aplane(mask))*voxelVolume;

    % 吸收能量及占入射总能量的百分比
    absorbedEnergy(j) = absorbedFraction*inputEnergy;
    absorbedPercent(j) = absorbedFraction*100;
end

disp(table(depthsCm(:), actualDepthCm(:), ...
    absorbedEnergy(:), absorbedPercent(:), ...
    'VariableNames', {'RequestedDepth_cm','ActualLayerDepth_cm', ...
                      'AbsorbedEnergy_J','AbsorbedPercent'}));

figure;
plot(actualDepthCm, absorbedPercent, 'o-', 'LineWidth', 1.5);
xlabel('所选体素层中心的皮下深度 [cm]');
ylabel('该区域吸收能量占入射总能量 [%]');
title(sprintf('半径 %g cm，厚度 %g cm，照射 %g s', ...
    circleRadiusCm, dz, exposureSeconds));
grid on;