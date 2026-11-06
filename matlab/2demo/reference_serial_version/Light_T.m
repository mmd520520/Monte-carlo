%% 第三步：设置运行条件并初始化 对后续所用到的参数进行初始化
% 所有长度单位均为 mm
% 依赖前面建立的 T、Nx、Ny、Nz、dx、dz 和 tissue

%% 1. 模拟规模
Nphotons = 1e6;       % 发射100万个光子包
rng(1, 'twister');    % 固定随机种子，方便复现结果

%% 2. 体素参数
dy = dx;
voxelVolume = dx * dy * dz;  % mm^3
surfaceArea = dx * dy;       % mm^2

%% 3. 光源参数
source.wavelength = 500;     % nm
source.type = 'uniform_disk';

source.diameter = 1;      % 光斑直径，mm
source.radius = source.diameter / 2;

source.x = 0;               % 光斑中心
source.y = 0;
source.z = zsurf;           % 皮肤表面：z = 1 mm


%%
% 垂直向组织内部入射，沿 +z 方向 
source.ux = 0;
source.uy = 0;
source.uz = 1;

% 4. 入射表面的镜面反射
n_air = tissue(1).n;
n_skin = tissue(5).n;       % 表皮折射率

Rsp = ((n_air - n_skin) / (n_air + n_skin))^2;

% 后续从表皮内部发射，初始权重扣除镜面反射损失
source.W0 = 1 - Rsp;
%%
%%角度入射
% baseDir = fileparts(mfilename('fullpath'));
% run(fullfile(baseDir, 'oblique_shot.m'));


% 避免光子恰好落在空气/表皮边界上
positionEpsilon = 1e-9;     % mm
source.zLaunch = zsurf + positionEpsilon;

%% 5. 轮盘赌参数
roulette.threshold = 0.001;
roulette.chance = 0.10;

%% 6. 边界条件
% 本模型选择：穿出计算区域即记录逃逸并终止
boundary.top = 'escape';
boundary.bottom = 'escape';
boundary.side = 'escape';

% 组织内部折射率变化，以及皮肤/空气界面：
% 后续传播时按 Fresnel 反射、折射处理

%% 7. 累计吸收数组
% Araw(ix,iy,iz)：所有光子在各体素沉积的原始权重之和
% 尚未除以光子数和体素体积
Araw = zeros(Nx, Ny, Nz, 'double');

%% 8. 表面逃逸数组
% 保存原始逃逸权重，后续再归一化
Rraw = zeros(Nx, Ny);       % 从皮肤上表面逃出的光
Traw = zeros(Nx, Ny);       % 从计算区域底面逃出的光

% 四个侧面逃逸的总权重
sideEscapeRaw = 0;

%% 9. 统计量
Nlaunched = 0;             % 已发射光子包数
Nterminated = 0;           % 已结束光子包数

% 镜面反射的总权重，单独记录
specularRaw = Nphotons * Rsp;