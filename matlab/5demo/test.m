% 示例：皮下1 cm处、半径2 cm、一层体素厚度的吸收比
depthCm = 1;
radiusCm = 2;

dx = results.x(2)-results.x(1);
dy = results.y(2)-results.y(1);
dz = results.z(2)-results.z(1);

[~,ix] = min(abs(results.x));
[~,iy] = min(abs(results.y));
iz = find(squeeze(results.tissueLabels(ix,iy,:)) > 1, 1);
skinZ = results.z(iz)-dz/2;

[~,kz] = min(abs(results.z-(skinZ+depthCm)));

[X,Y] = ndgrid(results.x, results.y);
labels = results.tissueLabels(:,:,kz);
mask = (X.^2+Y.^2 <= radiusCm^2) & (labels > 1);

Aplane = results.A(:,:,kz);

% results.A已按入射总能量归一化，乘体积就是吸收比例
layerFraction = sum(Aplane(mask))*dx*dy*dz;

fprintf('实际层中心皮下深度：%.4f cm\n', results.z(kz)-skinZ);
fprintf('薄层厚度：%.4f cm\n', dz);
fprintf('该薄层吸收占输入：%.6f %%\n', layerFraction*100);
fprintf('全部组织吸收占输入：%.6f %%\n', ...
    results.absorbedFraction*100);

% 子区域吸收不能超过全部组织吸收
assert(layerFraction <= results.absorbedFraction+1e-10, ...
    '局部吸收超过总吸收，请检查结果数据。');