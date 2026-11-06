%% 4. 斜入射：Fresnel反射率与折射方向

% 两侧介质的折射率
n_air = tissue(1).n;
n_skin = tissue(5).n;

% 空气中的入射方向
theta_i_deg = 45;       % 入射角，相对于表面法线，单位：度
phi_deg = 0;           % 方位角；0表示在x-z平面内入射

theta_i = deg2rad(theta_i_deg);
phi = deg2rad(phi_deg);

assert(theta_i_deg >= 0 && theta_i_deg < 90, ...
    '入射角必须在0到90度之间，不包括90度。');

% 保存空气中的入射方向
source.uAir = [ ...
    sin(theta_i) * cos(phi), ...
    sin(theta_i) * sin(phi), ...
    cos(theta_i)];

% Snell定律：计算进入皮肤后的折射角
sin_theta_t = (n_air / n_skin) * sin(theta_i);

assert(sin_theta_t < 1, ...
    '当前条件发生全内反射，没有进入组织的传播光。');

theta_t = asin(sin_theta_t);

cos_theta_i = cos(theta_i);
cos_theta_t = cos(theta_t);

% s偏振反射率
Rs = ((n_air * cos_theta_i - n_skin * cos_theta_t) / ...
      (n_air * cos_theta_i + n_skin * cos_theta_t))^2;

% p偏振反射率
Rp = ((n_skin * cos_theta_i - n_air * cos_theta_t) / ...
      (n_skin * cos_theta_i + n_air * cos_theta_t))^2;

% 非偏振光：取两种偏振反射率的平均
Rsp = (Rs + Rp) / 2;

% 进入组织的初始权重
source.W0 = 1 - Rsp;

% 进入组织后，必须使用折射方向
source.ux = sin(theta_t) * cos(phi);
source.uy = sin(theta_t) * sin(phi);
source.uz = cos(theta_t);

fprintf('空气入射角：%.2f 度\n', theta_i_deg);
fprintf('皮肤折射角：%.2f 度\n', rad2deg(theta_t));
fprintf('镜面反射率：%.4f\n', Rsp);
fprintf('进入组织的权重：%.4f\n', source.W0);