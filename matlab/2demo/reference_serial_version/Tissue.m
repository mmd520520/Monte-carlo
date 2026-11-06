%clear;clc;

Ny = 400;
Nx = Ny;
Nz = Ny;
% 由上到下 空气：1 血管：3 真皮：4 表皮：5 
dx = 0.010;  % mm，体素大小为 10 μm
dz = dx;

x = ((1:Nx)' - Nx/2) * dx;
z = (1:Nz)' * dz;

T = double(zeros(Nx, Ny, Nz));
T = T + 4;  % 默认填充真皮：4 = dermis

zsurf = 1;  % 空气/皮肤表面的位置，单位 mm

for iz = 1:Nz

    % 空气：1 = air
    if iz <= round(zsurf/dz)
        T(:, :, iz) = 1;
    end

    % 表皮：5 = epidermis，厚度 100 μm
    if iz > round(zsurf/dz) && ...
       iz <= round((zsurf + 0.100)/dz)
        T(:, :, iz) = 5;
    end

    % 血管：沿 y 轴延伸的圆柱
    xc = 0;            % 血管中心 x 坐标，mm
    zc = Nz/2 * dz;    % 血管中心 z 坐标，mm
    vesselradius = 0.5; % 血管半径，mm

    for ix = 1:Nx
        xd = x(ix) - xc;
        zd = z(iz) - zc;
        r = sqrt(xd^2 + zd^2);

        if r <= vesselradius
            T(ix, :, iz) = 3;  % 3 = blood
        end
    end
end


%%Figure 
%% 可视化：组织的 x-z 侧面截面

% 血管沿 y 方向延伸，取中间位置的截面
iy = Ny/2;
Txz = squeeze(T(:, iy, :))';

% 将组织编号转换成连续的颜色编号
C = zeros(Nz, Nx);
C(Txz == 1) = 1;  % 空气
C(Txz == 5) = 2;  % 表皮
C(Txz == 4) = 3;  % 真皮
C(Txz == 3) = 4;  % 血管

figure('Color', 'w');
imagesc(x, z, C);

colormap([
    0.98 0.97 0.94;   % 空气：米白
    0.72 0.66 0.52;   % 表皮：棕色
    0.93 0.79 0.77;   % 真皮：粉色
    0.90 0.00 0.00    % 血管：红色
]);
caxis([0.5 4.5]);

axis image;
set(gca, 'YDir', 'reverse', 'FontSize', 12);
xlim([-2 2]);
ylim([0 4]);

xlabel('x [mm]');
ylabel('z [mm]');
title('Tissue model: x-z cross-section');
box on;

% 添加组织标签
text(-1.8, 0.5, 'Air');
text(-1.8, 1.2, 'Epidermis');
text(-1.8, 2.8, 'Dermis');

text(xc, zc, {'Blood', 'vessel'}, ...
    'Color', 'w', ...
    'HorizontalAlignment', 'center');










