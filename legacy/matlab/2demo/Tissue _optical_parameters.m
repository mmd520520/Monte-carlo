% 第二步：组织光学参数 对第一步构建的体素进行属性赋值
% 波长：500 nm
% mua、mus、musp 的单位统一为 mm^(-1)
% musp 是约化散射系数，mus 才是传播计算使用的散射系数
% mus = musp / (1-g)

wavelength = 500;  % nm

tissue = repmat(struct( ...
    'name', '', ...
    'mua', 0, ...
    'mus', 0, ...
    'g',   0, ...
    'n',   1), 1, 5);

% 1：空气，按无吸收、无散射介质处理
tissue(1).name = 'air';
tissue(1).mua  = 0;
tissue(1).mus  = 0;
tissue(1).g    = 0;
tissue(1).n    = 1.0;

% 3：血液
tissue(3).name = 'blood';
tissue(3).mua  = 11.20;
tissue(3).g    = 0.90;
tissue(3).mus  = 1.00 / (1 - tissue(3).g);  % 10 mm^-1
tissue(3).n    = 1.4;

% 4：真皮
tissue(4).name = 'dermis';
tissue(4).mua  = 0.02241645;
tissue(4).g    = 0.90;
tissue(4).mus  = 4.24 / (1 - tissue(4).g);  % 42.4 mm^-1
tissue(4).n    = 1.4;

% 5：表皮
tissue(5).name = 'epidermis';
tissue(5).mua  = 2.03701875;
tissue(5).g    = 0.90;
tissue(5).mus  = 2.00 / (1 - tissue(5).g);  % 20 mm^-1
tissue(5).n    = 1.4;