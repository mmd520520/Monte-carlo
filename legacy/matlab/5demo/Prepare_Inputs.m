function [model, tissue, config, tallies] = Prepare_Inputs(photonCount, smokeTest, seed)
    % 接口适配：原样执行用户的三个脚本，再转换为后续函数的输入。
    % 所有脚本变量限制在本函数工作区中，不依赖基础工作区。 clear;clc;
    if nargin < 1
        photonCount = [];
    end
    if nargin < 2
        smokeTest = false;
    end
    if nargin < 3
        seed = 1;
    end

    baseDir = fileparts(mfilename('fullpath'));
    % 显式声明由原脚本提供的变量；脚本执行后必须通过有效性检查。
    T = [];
    Nx = [];
    Ny = [];
    Nz = [];
    dx = [];
    dz = [];
    tissue = [];
    buildOnly = true;
    run(fullfile(baseDir, 'Tissue_knee.m'));
    % MATLAB脚本文件名中有空格，故读取这份固定的本地参数文件执行。
    eval(fileread(fullfile(baseDir, 'Tissue _optical_parameters.m')));
    assert(~isempty(T) && numel(tissue) == 4, '原始脚本未提供有效模型或参数。');%%检测进程bug

    if smokeTest
        stride=2;
        T=T(1:stride:end,1:stride:end,1:stride:end);
        [Nx,Ny,Nz]=size(T); dx=dx*stride; dy=dy*stride; dz=dz*stride;
        x=((1:Nx)-0.5)*dx-Nx*dx/2;
        y=((1:Ny)-0.5)*dy-Ny*dy/2;
        z=((1:Nz)-0.5)*dz;
    end

    run(fullfile(baseDir, 'Light_T.m'));

    if ~isempty(photonCount)
        Nphotons = photonCount;
    end

    %%违规检测 查看输入是否正确
    validateattributes(Nphotons, {'numeric'}, ...
        {'scalar', 'integer', 'positive', 'finite'});
    validateattributes(seed, {'numeric'}, ...
        {'scalar', 'integer', 'nonnegative', 'finite'});
    assert(strcmp(source.type, 'uniform_disk'));
    % 初始方向稍后由thetaDeg/phiDeg统一计算，支持斜入射。
    assert(source.wavelength == wavelength);
    assert(strcmp(boundary.top, 'escape'));
    assert(strcmp(boundary.bottom, 'escape'));
    assert(strcmp(boundary.side, 'escape'));
    assert(all(ismember(unique(T(:)), 1:4)));
    assert(all(ismember(2:4, unique(T(:))')), 'Missing knee tissue labels.');

    model.T = uint8(T);
    model.Nx = Nx;
    model.Ny = Ny;
    model.Nz = Nz;
    model.dx = dx;
    model.dy = dy;
    model.dz = dz;
    model.size = [Nx, Ny, Nz];
    model.spacing = [dx, dy, dz];
    model.offset = [Nx * dx / 2, Ny * dy / 2, 0];
    model.x = x;
    model.z = z;
    model.y = y;
    model.lengthUnit = 'cm';
    model.zsurf = zsurf;
    model.airLayerCount = round(zsurf / dz);

    config.Nphotons = Nphotons;
    config.seed = seed;
    config.source = source;
    config.Rsp = Rsp;
    config.roulette = roulette;
    config.boundary = boundary;
    config.voxelVolume = voxelVolume;
    config.surfaceArea = surfaceArea;

    tallies.Araw = Araw;
    tallies.Rraw = Rraw;
    tallies.Traw = Traw;
    tallies.sideEscapeRaw = sideEscapeRaw;
    tallies.Nlaunched = Nlaunched;
    tallies.Nterminated = Nterminated;
    tallies.AirPathRaw = zeros(Nx, Ny, Nz);
    tallies.rouletteBalanceRaw = 0;
    tallies.boundaryEvents = 0;
    tallies.scatteringEvents = 0;
    tallies.airEscapedPackets = 0;
end
