clear; clc; close all;

S = load('fullhead_atlas.mat');
T = uint8(S.USC_atlas);

figure('Color','w','Renderer','opengl');
ax = axes;
hold(ax,'on');

% 组织编号、颜色和透明度
ids = [1 2 4 5];
colors = [
    0.95 0.70 0.58   % 头皮
    0.92 0.87 0.68   % 颅骨
    0.80 0.42 0.48   % 灰质
    0.96 0.94 0.80   % 白质
];
opacity = [0.08 0.12 0.65 1.0];

for k = 1:numel(ids)
    mask = T == ids(k);

    % 转换数组顺序，使绘图x、y对应模型的第一、二维
    V = permute(single(mask),[2 1 3]);
    fv = isosurface(V,0.5);

    if ~isempty(fv.vertices)
        patch(ax,fv, ...
            'FaceColor',colors(k,:), ...
            'FaceAlpha',opacity(k), ...
            'EdgeColor','none', ...
            'DisplayName',num2str(ids(k)));
    end
end

axis(ax,'equal');
axis(ax,'tight');
axis(ax,'vis3d');

xlabel('x 体素索引');
ylabel('y 体素索引');
zlabel('z 体素索引');
title('三维头部模型  鼠标拖动旋转');

view(3);
camlight('headlight');
lighting gouraud;
material dull;

rotate3d(gcf,'on');


%% 模型各组成图片
%% 加载模型
S = load('fullhead_atlas.mat');
vol = S.USC_atlas;

names = {'头皮', '颅骨', '脑脊液', '灰质', '白质', '内部空气腔'};
colors = [
    0.95  0.65  0.45;  % 头皮：橙色
    0.90  0.80  0.35;  % 颅骨：黄色
    0.20  0.65  0.95;  % 脑脊液：蓝色
    0.65  0.45  0.80;  % 灰质：紫色
    0.85  0.85  0.85;  % 白质：浅灰色
    0.25  0.80  0.55   % 内部空气腔：绿色
];

voxelSize = 1;  % mm，与官方示例一致
outDir = 'head_tissue_figures';
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

%% 分别绘制六类组织
for label = 1:6
    mask = (vol == label);

    if ~any(mask(:))
        warning('标签 %d 没有体素，跳过。', label);
        continue;
    end

    % 外围补零，保证接触数组边缘的组织表面也能闭合
    padded = zeros(size(mask) + 2, 'single');
    padded(2:end-1, 2:end-1, 2:end-1) = single(mask);

    % MATLAB isosurface 的坐标顺序是：列、行、页。
    % 交换前两维，使绘图坐标对应 vol 的 x、y、z。
    fv = isosurface(permute(padded, [2 1 3]), 0.5);

    % 将体素中心设置在 0.5、1.5、2.5 ... mm
    fv.vertices = (fv.vertices - 1.5) * voxelSize;

    fig = figure('Color', 'w', ...
        'Name', names{label}, ...
        'Position', [100 + 30*label, 100, 850, 750]);

    patch(fv, ...
        'FaceColor', colors(label,:), ...
        'EdgeColor', 'none', ...
        'FaceAlpha', 1);

    axis equal;
    axis vis3d;
    xlim([0 size(vol,1)*voxelSize]);
    ylim([0 size(vol,2)*voxelSize]);
    zlim([0 size(vol,3)*voxelSize]);

    xlabel('x (mm)');
    ylabel('y (mm)');
    zlabel('z (mm)');
    title(sprintf('%d：%s', label, names{label}), 'FontSize', 16);

    view(135, 25);
    camlight('headlight');
    lighting gouraud;
    material dull;
    grid on;
    rotate3d on;

    % 保存图片
    filename = fullfile(outDir, sprintf('tissue_%d.png', label));
    exportgraphics(fig, filename, ...
        'Resolution', 300, 'BackgroundColor', 'white');
end